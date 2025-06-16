from flask import Blueprint, request, jsonify
from src.api.services.user_service import UserService
from src.utils.jwt_helper import admin_required, login_required

class UserController:
    def __init__(self):
        self.bp = Blueprint('user', __name__, url_prefix='/users')
        self.setup_routes()
        self.user_service = UserService()

    def setup_routes(self):
        self.bp.route('/', methods=['GET'])(login_required(self.list_users))
        self.bp.route('/<int:user_id>', methods=['GET'])(login_required(self.get_user))
        self.bp.route('/', methods=['POST'])(admin_required(self.create_user))
        self.bp.route('/<int:user_id>', methods=['PUT'])(admin_required(self.update_user))
        self.bp.route('/<int:user_id>', methods=['DELETE'])(admin_required(self.delete_user))

    def list_users(self):
        # Get query parameters with defaults
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', None)
        role = request.args.get('role', None)
        divisi = request.args.get('divisi', None)

        # Validate pagination parameters
        if page < 1:
            return jsonify({"message": "Page number must be greater than 0"}), 400
        if per_page < 1 or per_page > 100:
            return jsonify({"message": "Items per page must be between 1 and 100"}), 400

        # Get users with pagination and filters
        result = self.user_service.get_users(
            page=page,
            per_page=per_page,
            search=search,
            role=role,
            divisi=divisi
        )

        # Format user list
        user_list = [{
            "id": u.id,
            "username": u.username,
            "nama_lengkap": u.nama_lengkap,
            "role": u.role,
            "divisi": u.divisi
        } for u in result["users"]]

        return jsonify({
            "users": user_list,
            "pagination": result["pagination"]
        }), 200

    def get_user(self, user_id):
        user = self.user_service.get_user(user_id)
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

    def create_user(self):
        data = request.get_json()
        
        # Validasi input
        required_fields = ['username', 'password', 'nama_lengkap', 'role', 'divisi']
        for field in required_fields:
            if field not in data:
                return jsonify({"message": f"Field {field} is required"}), 400

        user, error = self.user_service.create_user(
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

    def update_user(self, user_id):
        data = request.get_json()
        user, error = self.user_service.update_user(user_id, data)

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

    def delete_user(self, user_id):
        success, error = self.user_service.delete_user(user_id)

        if error:
            return jsonify({"message": error}), 404

        return jsonify({"message": "User deleted successfully"}), 200

# Create controller instance
user_controller = UserController()
user_bp = user_controller.bp