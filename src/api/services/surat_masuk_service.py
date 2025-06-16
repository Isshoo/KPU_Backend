from src.database.config import SessionLocal
from src.database.models.surat_masuk import SuratMasuk
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from sqlalchemy import or_

class SuratMasukService:
    def __init__(self):
        self.upload_folder = "src/storage/surat_masuk"
        os.makedirs(self.upload_folder, exist_ok=True)

    def get_surat_masuk(self, page=1, per_page=10, search=None, start_date=None, end_date=None):
        session = SessionLocal()
        try:
            # Base query
            query = session.query(SuratMasuk)

            # Apply filters if provided
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        SuratMasuk.nomor_surat.ilike(search_term),
                        SuratMasuk.pengirim.ilike(search_term),
                        SuratMasuk.perihal.ilike(search_term),
                        SuratMasuk.ditujukan_kepada.ilike(search_term)
                    )
                )
            
            if start_date:
                query = query.filter(SuratMasuk.tanggal_terima >= start_date)
            
            if end_date:
                query = query.filter(SuratMasuk.tanggal_terima <= end_date)

            # Get total count before pagination
            total = query.count()

            # Apply pagination
            surat_list = query.order_by(SuratMasuk.tanggal_terima.desc())\
                             .offset((page - 1) * per_page)\
                             .limit(per_page)\
                             .all()

            # Calculate pagination info
            total_pages = (total + per_page - 1) // per_page

            return {
                "surat_list": surat_list,
                "pagination": {
                    "total": total,
                    "per_page": per_page,
                    "current_page": page,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            }
        finally:
            session.close()

    def get_surat_by_id(self, surat_id):
        session = SessionLocal()
        try:
            surat = session.query(SuratMasuk).filter(SuratMasuk.id == surat_id).first()
            return surat
        finally:
            session.close()

    def create_surat(self, data, file=None, user_id=None):
        session = SessionLocal()
        try:
            # Handle file upload if provided
            if not file:
                return None, "File surat wajib diunggah"

            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(self.upload_folder, f"{timestamp}_{filename}")
            file.save(file_path)

            # Create new surat masuk
            new_surat = SuratMasuk(
                nomor_surat=data['nomor_surat'],
                tanggal_surat=datetime.strptime(data['tanggal_surat'], '%Y-%m-%d'),
                tanggal_terima=datetime.strptime(data['tanggal_terima'], '%Y-%m-%d'),
                pengirim=data['pengirim'],
                perihal=data['perihal'],
                ditujukan_kepada=data['ditujukan_kepada'],
                keterangan=data.get('keterangan'),
                file_path=file_path,
                inserted_by_id=user_id,
                array_id_dibaca_oleh=[]
            )
            
            session.add(new_surat)
            session.commit()
            session.refresh(new_surat)
            return new_surat, None
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()

    def update_surat(self, surat_id, data, file=None, user_id=None):
        session = SessionLocal()
        try:
            surat = session.query(SuratMasuk).filter(SuratMasuk.id == surat_id).first()
            if not surat:
                return None, "Surat tidak ditemukan"

            # Handle file upload if provided
            if file:
                # Delete old file if exists
                if surat.file_path and os.path.exists(surat.file_path):
                    os.remove(surat.file_path)
                
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = os.path.join(self.upload_folder, f"{timestamp}_{filename}")
                file.save(file_path)
                surat.file_path = file_path

            # Update fields
            if 'nomor_surat' in data:
                surat.nomor_surat = data['nomor_surat']
            if 'tanggal_surat' in data:
                surat.tanggal_surat = datetime.strptime(data['tanggal_surat'], '%Y-%m-%d')
            if 'tanggal_terima' in data:
                surat.tanggal_terima = datetime.strptime(data['tanggal_terima'], '%Y-%m-%d')
            if 'pengirim' in data:
                surat.pengirim = data['pengirim']
            if 'perihal' in data:
                surat.perihal = data['perihal']
            if 'ditujukan_kepada' in data:
                surat.ditujukan_kepada = data['ditujukan_kepada']
            if 'keterangan' in data:
                surat.keterangan = data['keterangan']
            
            session.commit()
            session.refresh(surat)
            return surat, None
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()

    def mark_as_read(self, surat_id, user_id):
        session = SessionLocal()
        try:
            surat = session.query(SuratMasuk).filter(SuratMasuk.id == surat_id).first()
            if not surat:
                return False, "Surat tidak ditemukan"

            if not surat.array_id_dibaca_oleh:
                surat.array_id_dibaca_oleh = []
            
            if user_id not in surat.array_id_dibaca_oleh:
                surat.array_id_dibaca_oleh.append(user_id)
                session.commit()
            
            return True, None
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def delete_surat(self, surat_id):
        session = SessionLocal()
        try:
            surat = session.query(SuratMasuk).filter(SuratMasuk.id == surat_id).first()
            if not surat:
                return False, "Surat tidak ditemukan"

            # Delete file if exists
            if surat.file_path and os.path.exists(surat.file_path):
                os.remove(surat.file_path)

            session.delete(surat)
            session.commit()
            return True, None
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

# Create a singleton instance
surat_masuk_service = SuratMasukService() 