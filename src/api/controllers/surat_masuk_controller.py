from flask import Blueprint, request, jsonify, send_file
from src.api.services.surat_masuk_service import SuratMasukService
from src.utils.jwt_helper import login_required, admin_required
from datetime import datetime
import os

class SuratMasukController:
    def __init__(self):
        self.bp = Blueprint('surat_masuk', __name__, url_prefix='/surat-masuk')
        self.setup_routes()
        self.surat_masuk_service = SuratMasukService()

    def setup_routes(self):
        self.bp.route('/', methods=['GET'])(login_required(self.list_surat))
        self.bp.route('/<int:surat_id>', methods=['GET'])(login_required(self.get_surat))
        self.bp.route('/', methods=['POST'])(login_required(self.create_surat))
        self.bp.route('/<int:surat_id>', methods=['PUT'])(login_required(self.update_surat))
        self.bp.route('/<int:surat_id>', methods=['DELETE'])(login_required(self.delete_surat))
        self.bp.route('/<int:surat_id>/file', methods=['GET'])(login_required(self.get_file))
        self.bp.route('/<int:surat_id>/read', methods=['POST'])(login_required(self.mark_as_read))

    def list_surat(self):
        try:
            # Get query parameters with defaults
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            search = request.args.get('search', None)
            start_date = request.args.get('start_date', None)
            end_date = request.args.get('end_date', None)

            # Convert dates if provided
            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            if end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')

            # Validate pagination parameters
            if page < 1:
                return jsonify({"status": "error", "message": "Page number must be greater than 0"}), 400
            if per_page < 1 or per_page > 100:
                return jsonify({"status": "error", "message": "Items per page must be between 1 and 100"}), 400

            # Get surat with pagination and filters
            result = self.surat_masuk_service.get_surat_masuk(
                page=page,
                per_page=per_page,
                search=search,
                start_date=start_date,
                end_date=end_date
            )

            # Format surat list
            surat_list = [{
                "id": s.id,
                "nomor_surat": s.nomor_surat,
                "tanggal_surat": s.tanggal_surat.strftime('%Y-%m-%d'),
                "tanggal_terima": s.tanggal_terima.strftime('%Y-%m-%d'),
                "pengirim": s.pengirim,
                "perihal": s.perihal,
                "ditujukan_kepada": s.ditujukan_kepada,
                "keterangan": s.keterangan,
                "inserted_by": s.inserted_by.nama_lengkap if s.inserted_by else None,
                "inserted_at": s.inserted_at.strftime('%Y-%m-%d %H:%M:%S'),
                "dibaca_oleh": [user.nama_lengkap for user in s.dibaca_oleh] if s.dibaca_oleh else []
            } for s in result["surat_list"]]

            return jsonify({
                "status": "success",
                "data": {
                    "surat_list": surat_list,
                    "pagination": result["pagination"]
                }
            }), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    def get_surat(self, surat_id):
        try:
            surat = self.surat_masuk_service.get_surat_by_id(surat_id)
            if not surat:
                return jsonify({"status": "error", "message": "Surat tidak ditemukan"}), 404

            surat_dict = {
                "id": surat.id,
                "nomor_surat": surat.nomor_surat,
                "tanggal_surat": surat.tanggal_surat.strftime('%Y-%m-%d'),
                "tanggal_terima": surat.tanggal_terima.strftime('%Y-%m-%d'),
                "pengirim": surat.pengirim,
                "perihal": surat.perihal,
                "ditujukan_kepada": surat.ditujukan_kepada,
                "keterangan": surat.keterangan,
                "inserted_by": surat.inserted_by.nama_lengkap if surat.inserted_by else None,
                "inserted_at": surat.inserted_at.strftime('%Y-%m-%d %H:%M:%S'),
                "dibaca_oleh": [user.nama_lengkap for user in surat.dibaca_oleh] if surat.dibaca_oleh else []
            }

            return jsonify({"status": "success", "data": surat_dict}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    def create_surat(self):
        try:
            # Get form data
            data = request.form.to_dict()
            file = request.files.get('file')

            # Validate required fields
            required_fields = ['nomor_surat', 'tanggal_surat', 'tanggal_terima', 'pengirim', 'perihal', 'ditujukan_kepada']
            for field in required_fields:
                if field not in data:
                    return jsonify({"status": "error", "message": f"Field {field} is required"}), 400

            # Create surat
            surat, error = self.surat_masuk_service.create_surat(
                data=data,
                file=file,
                user_id=request.current_user.id
            )

            if error:
                return jsonify({"status": "error", "message": error}), 400

            return jsonify({
                "status": "success",
                "message": "Surat berhasil dibuat",
                "data": {
                    "id": surat.id,
                    "nomor_surat": surat.nomor_surat,
                    "tanggal_surat": surat.tanggal_surat.strftime('%Y-%m-%d'),
                    "tanggal_terima": surat.tanggal_terima.strftime('%Y-%m-%d'),
                    "pengirim": surat.pengirim,
                    "perihal": surat.perihal,
                    "ditujukan_kepada": surat.ditujukan_kepada
                }
            }), 201
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    def update_surat(self, surat_id):
        try:
            # Get form data
            data = request.form.to_dict()
            file = request.files.get('file')

            # Update surat
            surat, error = self.surat_masuk_service.update_surat(
                surat_id=surat_id,
                data=data,
                file=file,
                user_id=request.current_user.id
            )

            if error:
                return jsonify({"status": "error", "message": error}), 400

            return jsonify({
                "status": "success",
                "message": "Surat berhasil diperbarui",
                "data": {
                    "id": surat.id,
                    "nomor_surat": surat.nomor_surat,
                    "tanggal_surat": surat.tanggal_surat.strftime('%Y-%m-%d'),
                    "tanggal_terima": surat.tanggal_terima.strftime('%Y-%m-%d'),
                    "pengirim": surat.pengirim,
                    "perihal": surat.perihal,
                    "ditujukan_kepada": surat.ditujukan_kepada
                }
            }), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    def delete_surat(self, surat_id):
        try:
            success, error = self.surat_masuk_service.delete_surat(surat_id)

            if error:
                return jsonify({"status": "error", "message": error}), 404

            return jsonify({"status": "success", "message": "Surat berhasil dihapus"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    def get_file(self, surat_id):
        try:
            surat = self.surat_masuk_service.get_surat_by_id(surat_id)
            if not surat or not surat.file_path:
                return jsonify({"status": "error", "message": "File tidak ditemukan"}), 404

            if not os.path.exists(surat.file_path):
                return jsonify({"status": "error", "message": "File tidak ditemukan di server"}), 404

            return send_file(
                surat.file_path,
                as_attachment=True,
                download_name=os.path.basename(surat.file_path)
            )
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    def mark_as_read(self, surat_id):
        try:
            success, error = self.surat_masuk_service.mark_as_read(
                surat_id=surat_id,
                user_id=request.current_user.id
            )

            if error:
                return jsonify({"status": "error", "message": error}), 404

            return jsonify({"status": "success", "message": "Surat ditandai sebagai telah dibaca"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

# Create controller instance
surat_masuk_controller = SuratMasukController()
surat_masuk_bp = surat_masuk_controller.bp 