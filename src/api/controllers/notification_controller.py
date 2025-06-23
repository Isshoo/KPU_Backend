from flask import Blueprint, jsonify, request
from src.api.services.notification_service import NotificationService
from src.utils.jwt_helper import login_required

class NotificationController:
    def __init__(self):
        self.bp = Blueprint('notifications', __name__, url_prefix='/notifications')
        self.notification_service = NotificationService()
        self.setup_routes()

    def setup_routes(self):
        self.bp.route('/', methods=['GET'])(login_required(self.get_notifications))

    def get_notifications(self):
        try:
            user_id = request.current_user.id
            notifications, error = self.notification_service.get_unread_notifications(user_id)

            if error:
                return jsonify({"status": "error", "message": error}), 404

            return jsonify({
                "status": "success",
                "data": {
                    "notifications": notifications,
                    "unread_count": len(notifications)
                }
            }), 200

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

# Create controller instance
notification_controller = NotificationController()
notification_bp = notification_controller.bp 