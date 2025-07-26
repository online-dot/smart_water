# app/routes/user/__init__.py
from flask import Blueprint

user_bp = Blueprint('user', __name__)

@user_bp.route('/')
def user_home():
    return "User dashboard placeholder"
