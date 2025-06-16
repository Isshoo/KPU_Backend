from src.database.config import SessionLocal
from src.database.models import SuratKeluar, User
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from sqlalchemy import or_

class SuratKeluarService:
    def __init__(self):
        self.upload_folder = "src/storage/surat_keluar/"
        os.makedirs(self.upload_folder, exist_ok=True)

    def get_surat_keluar(self, page=1, per_page=10, search=None, start_date=None, end_date=None):
        db = SessionLocal()
        try:
            query = db.query(SuratKeluar)

            # Apply filters
            if search:
                search = f"%{search}%"
                query = query.filter(
                    or_(
                        SuratKeluar.nomor_surat.ilike(search),
                        SuratKeluar.perihal.ilike(search),
                        SuratKeluar.ditujukan_kepada.ilike(search)
                    )
                )

            if start_date:
                query = query.filter(SuratKeluar.tanggal_surat >= start_date)
            if end_date:
                query = query.filter(SuratKeluar.tanggal_surat <= end_date)

            # Get total count
            total = query.count()

            # Apply pagination
            surat_list = query.order_by(SuratKeluar.tanggal_surat.desc())\
                .offset((page - 1) * per_page)\
                .limit(per_page)\
                .all()

            return {
                "surat_list": surat_list,
                "pagination": {
                    "total": total,
                    "page": page,
                    "per_page": per_page,
                    "total_pages": (total + per_page - 1) // per_page
                }
            }
        finally:
            db.close()

    def get_surat_by_id(self, surat_id):
        db = SessionLocal()
        try:
            return db.query(SuratKeluar).filter(SuratKeluar.id == surat_id).first()
        finally:
            db.close()

    def create_surat(self, data, file, user_id):
        db = SessionLocal()
        try:
            if not file:
                return None, "File surat harus diupload"

            # Save file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            file_path = os.path.join(self.upload_folder, filename)
            file.save(file_path)

            # Create surat
            surat = SuratKeluar(
                nomor_surat=data['nomor_surat'],
                tanggal_surat=datetime.strptime(data['tanggal_surat'], '%Y-%m-%d'),
                tanggal_kirim=datetime.strptime(data['tanggal_kirim'], '%Y-%m-%d'),
                ditujukan_kepada=data['ditujukan_kepada'],
                perihal=data['perihal'],
                keterangan=data.get('keterangan'),
                file_path=file_path,
                inserted_by_id=user_id
            )

            db.add(surat)
            db.commit()
            db.refresh(surat)
            return surat, None
        except Exception as e:
            db.rollback()
            return None, str(e)
        finally:
            db.close()

    def update_surat(self, surat_id, data, file, user_id):
        db = SessionLocal()
        try:
            surat = db.query(SuratKeluar).filter(SuratKeluar.id == surat_id).first()
            if not surat:
                return None, "Surat tidak ditemukan"

            # Update fields
            if 'nomor_surat' in data:
                surat.nomor_surat = data['nomor_surat']
            if 'tanggal_surat' in data:
                surat.tanggal_surat = datetime.strptime(data['tanggal_surat'], '%Y-%m-%d')
            if 'tanggal_kirim' in data:
                surat.tanggal_kirim = datetime.strptime(data['tanggal_kirim'], '%Y-%m-%d')
            if 'ditujukan_kepada' in data:
                surat.ditujukan_kepada = data['ditujukan_kepada']
            if 'perihal' in data:
                surat.perihal = data['perihal']
            if 'keterangan' in data:
                surat.keterangan = data['keterangan']

            # Handle file upload if provided
            if file:
                # Delete old file if exists
                if surat.file_path and os.path.exists(surat.file_path):
                    os.remove(surat.file_path)

                # Save new file
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                file_path = os.path.join(self.upload_folder, filename)
                file.save(file_path)
                surat.file_path = file_path

            db.commit()
            db.refresh(surat)
            return surat, None
        except Exception as e:
            db.rollback()
            return None, str(e)
        finally:
            db.close()

    def delete_surat(self, surat_id):
        db = SessionLocal()
        try:
            surat = db.query(SuratKeluar).filter(SuratKeluar.id == surat_id).first()
            if not surat:
                return False, "Surat tidak ditemukan"

            # Delete file if exists
            if surat.file_path and os.path.exists(surat.file_path):
                os.remove(surat.file_path)

            db.delete(surat)
            db.commit()
            return True, None
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    def mark_as_read(self, surat_id, user_id):
        db = SessionLocal()
        try:
            surat = db.query(SuratKeluar).filter(SuratKeluar.id == surat_id).first()
            if not surat:
                return False, "Surat tidak ditemukan"

            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "User tidak ditemukan"

            if user not in surat.dibaca_oleh:
                surat.dibaca_oleh.append(user)
                db.commit()

            return True, None
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

# Create singleton instance
surat_keluar_service = SuratKeluarService() 