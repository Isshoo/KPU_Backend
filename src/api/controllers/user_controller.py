from flask import Blueprint, request, jsonify
from src.api.services import user_service
from src.utils.jwt_helper import admin_required, login_required

user_bp = Blueprint('user', __name__, url_prefix='/users')

@user_bp.route('/', methods=['GET'])
@login_required
def list_users():
    users = user_service.get_users()
    user_list = [{
        "id": u.id,
        "username": u.username,
        "nama_lengkap": u.nama_lengkap,
        "role": u.role,
        "divisi": u.divisi
    } for u in users]

    return jsonify({"users": user_list}), 200

@user_bp.route('/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    user = user_service.get_user(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    user_dict = {
        "id": user.id,
        "username": user.username,
        "nama_lengkap": user.nama_lengkap,
        "role": user.role,
        "divisi": user.divisi
    }

    return jsonify({"user": user_dict}), 200

@user_bp.route('/', methods=['POST'])
@admin_required
def create_user():
    data = request.get_json()
    
    # Validasi input
    required_fields = ['username', 'password', 'nama_lengkap', 'role', 'divisi']
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Field {field} is required"}), 400

    user, error = user_service.create_user(
        username=data['username'],
        password=data['password'],
        nama_lengkap=data['nama_lengkap'],
        role=data['role'],
        divisi=data['divisi']
    )

    if error:
        return jsonify({"message": error}), 400

    return jsonify({
        "message": "User created successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "nama_lengkap": user.nama_lengkap,
            "role": user.role,
            "divisi": user.divisi
        }
    }), 201

@user_bp.route('/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    data = request.get_json()
    user, error = user_service.update_user(user_id, data)

    if error:
        return jsonify({"message": error}), 400 if error == "User not found" else 404

    return jsonify({
        "message": "User updated successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "nama_lengkap": user.nama_lengkap,
            "role": user.role,
            "divisi": user.divisi
        }
    }), 200

@user_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    success, error = user_service.delete_user(user_id)

    if error:
        return jsonify({"message": error}), 404

    return jsonify({"message": "User deleted successfully"}), 200