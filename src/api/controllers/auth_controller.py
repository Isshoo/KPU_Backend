from flask import Blueprint, request, jsonify
from src.api.services import auth_service, user_service
from src.utils.jwt_helper import login_required, admin_required
import os
import uuid
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    token, error = auth_service.login(username, password)
    if error:
        return jsonify({"message": error}), 401

    return jsonify({"access_token": token}), 200

@auth_bp.route('/register', methods=['POST'])
@admin_required
def register():
    data = request.get_json()
    
    # Validasi input
    required_fields = ['nama_lengkap', 'role', 'divisi']
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Field {field} is required"}), 400

    user, error = auth_service.register_user(
        nama_lengkap=data['nama_lengkap'],
        role=data['role'],
        divisi=data['divisi']
    )

    if error:
        return jsonify({"message": error}), 400

    return jsonify({
        "message": "User registered successfully",
        "user": user
    }), 201

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not current_password or not new_password:
        return jsonify({"message": "Current password and new password are required"}), 400

    # Verifikasi password lama
    user = request.current_user
    if not check_password_hash(user.password_hash, current_password):
        return jsonify({"message": "Current password is incorrect"}), 401

    # Update password
    success, error = user_service.update_password(user.id, new_password)
    if error:
        return jsonify({"message": error}), 400

    return jsonify({"message": "Password updated successfully"}), 200