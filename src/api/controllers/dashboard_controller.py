from flask import Blueprint, jsonify
from src.api.services.dashboard_service import DashboardService
from src.utils.jwt_helper import admin_required, login_required

class DashboardController:
    def __init__(self):
        self.bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')
        self.setup_routes()
        self.dashboard_service = DashboardService()

    def setup_routes(self):
        self.bp.route('/stats/', methods=['GET'])(login_required(self.get_stats))

    def get_stats(self):
        try:
            stats = self.dashboard_service.get_stats()
            return jsonify({
                'status': 'success',
                'data': stats
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500 
    
dashboard_controller = DashboardController()
dashboard_bp = dashboard_controller.bp