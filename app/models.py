from .extensions import db
from datetime import datetime

class Meter(db.Model):
    __tablename__ = 'meter'

    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(50), unique=True, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(10), default="active")  # active/inactive

    # Relationships
    user = db.relationship('User', backref='meter', uselist=False)
    usage_logs = db.relationship('UsageLog', backref='meter', lazy=True)

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    account_type = db.Column(db.String(20), nullable=False)  # prepaid/postpaid
    balance = db.Column(db.Float, default=0.0)
    registered_on = db.Column(db.DateTime, default=datetime.utcnow)

    meter_id = db.Column(db.Integer, db.ForeignKey('meter.id'), nullable=False)

class UsageLog(db.Model):
    __tablename__ = 'usage_log'

    id = db.Column(db.Integer, primary_key=True)
    meter_id = db.Column(db.Integer, db.ForeignKey('meter.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    flow_liters = db.Column(db.Float, nullable=False)  # From ESP32
    balance_at_time = db.Column(db.Float, nullable=False)  # Recorded snapshot
    