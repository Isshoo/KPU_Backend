from flask import Flask
from flask_cors import CORS

from src.api.controllers.auth_controller import auth_bp
from src.api.controllers.user_controller import user_bp
from src.api.controllers.surat_masuk_controller import surat_masuk_bp
from src.api.controllers.surat_keluar_controller import surat_keluar_bp
from src.api.controllers.dashboard_controller import dashboard_bp
from src.api.controllers.notification_controller import notification_bp


def create_app():
    app = Flask(__name__)
    
    # Konfigurasi CORS
    CORS(app, resources={
        r"/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(surat_masuk_bp)
    app.register_blueprint(surat_keluar_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(notification_bp)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True)