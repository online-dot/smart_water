from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required
from ...extensions import db
from ...models import User, Meter, UsageLog  # Make sure UsageLog is correctly imported

admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')

# 🏠 Admin Dashboard Web Page
@admin_bp.route('/')
def admin_home():
    total_users = User.query.count()
    total_balance = db.session.query(db.func.sum(User.balance)).scalar() or 0.0
    low_balance_users = User.query.filter(User.balance < 20).all()
    inactive_meters = Meter.query.filter_by(status='inactive').all()
    
    return render_template('admin_dashboard.html',
                           total_users=total_users,
                           total_balance=total_balance,
                           low_balance_users=low_balance_users,
                           inactive_meters=inactive_meters)

# 🔵 Register User + Meter (JSON API)
@admin_bp.route('/add_user', methods=['POST'])
def add_user():
    try:
        data = request.get_json()
        required_fields = ['full_name', 'phone', 'account_type', 'location', 'serial_number']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f"Missing fields: {', '.join(missing_fields)}"}), 400

        existing_meter = Meter.query.filter_by(serial_number=data['serial_number']).first()
        if existing_meter:
            return jsonify({'error': 'Meter serial number is already in use'}), 400

        meter = Meter(
            serial_number=data['serial_number'],
            location=data['location']
        )
        db.session.add(meter)
        db.session.flush()

        user = User(
            full_name=data['full_name'],
            phone=data['phone'],
            email=data.get('email'),
            account_type=data['account_type'],
            balance=float(data.get('balance', 0.0)),
            meter_id=meter.id
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User and meter registered successfully'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


# 🔍 Web Views
@admin_bp.route('/users')
def get_all_users():
    users = User.query.all()
    return render_template('users.html', users=users)

@admin_bp.route('/meters')
def get_all_meters():
    meters = Meter.query.all()
    return render_template('meters.html', meters=meters)

@admin_bp.route('/low_balance_users')
def view_low_balance_users():
    users = User.query.filter(User.balance < 20).all()
    return render_template('low_balance.html', users=users)

@admin_bp.route('/inactive_meters')
def view_inactive_meters():
    meters = Meter.query.filter_by(status='inactive').all()
    return render_template('inactive_meters.html', meters=meters)

@admin_bp.route('/total_users')
def view_total_users():
    count = User.query.count()
    return render_template('total_users.html', total_users=count)

@admin_bp.route('/total_payments')
def view_total_payments():
    total = db.session.query(db.func.sum(User.balance)).scalar() or 0.0
    return render_template('total_payments.html', total_payments=total)


# 🛠️ Manual Admin Controls
@admin_bp.route('/update_status', methods=['POST'])
def update_status():
    meter_id = request.form['meter_id']
    new_status = request.form['status']

    meter = Meter.query.get(meter_id)
    if meter:
        meter.status = new_status
        db.session.commit()
        flash('Meter status updated successfully.', 'success')
    else:
        flash('Meter not found.', 'danger')
    return redirect(url_for('admin.get_all_meters'))

@admin_bp.route('/recharge_balance', methods=['POST'])
def recharge_balance():
    user_id = request.form['user_id']
    amount = float(request.form['amount'])

    user = User.query.get(user_id)
    if user:
        user.balance += amount
        db.session.commit()
        flash('User balance recharged successfully.', 'success')
    else:
        flash('User not found.', 'danger')
    return redirect(url_for('admin.get_all_users'))

@admin_bp.route('/toggle_valve', methods=['POST'])
def toggle_valve():
    meter_id = request.form['meter_id']
    action = request.form['action']  # open or close

    meter = Meter.query.get(meter_id)
    if meter:
        meter.status = 'open' if action == 'open' else 'closed'
        db.session.commit()
        flash(f'Valve {action}ed successfully.', 'success')
    else:
        flash('Meter not found.', 'danger')
    return redirect(url_for('admin.get_all_meters'))


# 🧪 Leak Reports Page (New Route Added)
@admin_bp.route('/leak_reports')
def leak_reports():
    logs = UsageLog.query.order_by(UsageLog.timestamp.desc()).all()
    return render_template('leak_reports.html', logs=logs)
