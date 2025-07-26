from flask import Blueprint, request, jsonify
from app.models import db, Meter, UsageLog

api_bp = Blueprint('api', __name__)

@api_bp.route('/log_usage', methods=['POST'])
def log_usage():
    data = request.get_json()

    serial = data.get('serial_number')
    flow = data.get('flow_liters')

    if not serial or flow is None:
        return jsonify({'status': 'error', 'message': 'Missing serial_number or flow_liters'}), 400

    # Find meter and linked user
    meter = Meter.query.filter_by(serial_number=serial).first()
    if not meter:
        return jsonify({'status': 'error', 'message': 'Meter not found'}), 404
    if not meter.user:
        return jsonify({'status': 'error', 'message': 'No user assigned to this meter'}), 404

    # Save usage log
    usage_log = UsageLog(
        meter_id=meter.id,
        flow_liters=flow,
        balance_at_time=meter.user.balance
    )
    db.session.add(usage_log)
    db.session.commit()

    # Leak detection logic
    leak_warning = None
    if meter.user.balance <= 0 and flow > 0:
        leak_warning = {
            'status': 'warning',
            'leak': True,
            'message': 'Water is flowing but balance is zero!'
        }
        return jsonify(leak_warning), 200

    return jsonify({'status': 'ok', 'leak': False})
