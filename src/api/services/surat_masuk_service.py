from src.database.config import SessionLocal
from src.database.models import SuratMasuk, User, SuratKeluar
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

class SuratMasukService:
    def __init__(self):
        self.upload_folder = "src/storage/surat_masuk/"
        os.makedirs(self.upload_folder, exist_ok=True)

    def _validate_nomor_surat(self, nomor_surat, exclude_id=None):
        """
        Validate if nomor surat already exists in database
        
        Args:
            nomor_surat (str): Nomor surat to validate
            exclude_id (int, optional): ID to exclude from validation (for updates)
            
        Returns:
            tuple: (is_valid, error_message)
        """
        db = SessionLocal()
        try:
            query = db.query(SuratMasuk).filter(SuratMasuk.nomor_surat == nomor_surat)
            
            if exclude_id:
                query = query.filter(SuratMasuk.id != exclude_id)
            
            existing_surat = query.first()
            
            if existing_surat:
                return False, f"Nomor surat '{nomor_surat}' sudah dimasukkan"
            
            query = db.query(SuratKeluar).filter(SuratKeluar.nomor_surat == nomor_surat)
            
            if exclude_id:
                query = query.filter(SuratKeluar.id != exclude_id)
            
            existing_surat = query.first()

            if existing_surat:
                return False, f"Nomor surat '{nomor_surat}' sudah dimasukkan di surat keluar"
            
            return True, None
        finally:
            db.close()

    def get_surat_masuk(self, page=1, per_page=10, search=None, start_date=None, end_date=None, divisi=None):
        db = SessionLocal()
        try:
            query = db.query(SuratMasuk).options(
                joinedload(SuratMasuk.inserted_by),
                joinedload(SuratMasuk.dibaca_oleh)
            )

            # Apply filters
            if search:
                search = f"%{search}%"
                query = query.filter(
                    or_(
                        SuratMasuk.nomor_surat.ilike(search),
                        SuratMasuk.perihal.ilike(search),
                        SuratMasuk.ditujukan_kepada.ilike(search),
                        SuratMasuk.keterangan.ilike(search)
                    )
                )

            if start_date:
                query = query.filter(SuratMasuk.tanggal_surat >= start_date)
            if end_date:
                query = query.filter(SuratMasuk.tanggal_surat <= end_date)

            if divisi:
                query = query.filter(SuratMasuk.divisi == divisi)

            # Get total count
            total = query.count()

            # Apply pagination
            surat_list = query.order_by(SuratMasuk.tanggal_surat.desc())\
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
            return db.query(SuratMasuk).options(
                joinedload(SuratMasuk.inserted_by),
                joinedload(SuratMasuk.dibaca_oleh)
            ).filter(SuratMasuk.id == surat_id).first()
        finally:
            db.close()

    def create_surat(self, data, file, user_id):
        db = SessionLocal()
        try:
            if not file:
                return None, "File surat harus diupload"

            # Validate nomor surat - check if already exists
            is_valid, error_message = self._validate_nomor_surat(data['nomor_surat'])
            if not is_valid:
                return None, error_message
            
            # Validate tanggal surat atau tanggal terima - check if tanggal surat or tanggal terima is greater than tanggal saat ini
            if datetime.strptime(data['tanggal_surat'], '%Y-%m-%d') > datetime.now() or datetime.strptime(data['tanggal_terima'], '%Y-%m-%d') > datetime.now():
                return None, "Tanggal surat atau tanggal terima tidak boleh lebih besar dari tanggal saat ini"

            # Save file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            file_path = os.path.join(self.upload_folder, filename)
            file.save(file_path)

            # Create surat
            surat = SuratMasuk(
                nomor_surat=data['nomor_surat'],
                tanggal_surat=datetime.strptime(data['tanggal_surat'], '%Y-%m-%d'),
                tanggal_terima=datetime.strptime(data['tanggal_terima'], '%Y-%m-%d'),
                pengirim=data['pengirim'],
                perihal=data['perihal'],
                ditujukan_kepada=data['ditujukan_kepada'],
                keterangan=data.get('keterangan'),
                divisi=data['divisi'],
                file_path=file_path,
                inserted_by_id=user_id,
                inserted_at=datetime.now(),
                dibaca_oleh_id=[]
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
            surat = db.query(SuratMasuk).filter(SuratMasuk.id == surat_id).first()
            if not surat:
                return None, "Surat tidak ditemukan"

            # Validate nomor surat if it's being updated - check if already exists (excluding current surat)
            if 'nomor_surat' in data and data['nomor_surat'] != surat.nomor_surat:
                is_valid, error_message = self._validate_nomor_surat(data['nomor_surat'], exclude_id=surat_id)
                if not is_valid:
                    return None, error_message
                
            # Validate tanggal surat atau tanggal terima - check if tanggal surat or tanggal terima is greater than tanggal saat ini
            if datetime.strptime(data['tanggal_surat'], '%Y-%m-%d') > datetime.now() or datetime.strptime(data['tanggal_terima'], '%Y-%m-%d') > datetime.now():
                return None, "Tanggal surat atau tanggal terima tidak boleh lebih besar dari tanggal saat ini"

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
            if 'divisi' in data:
                surat.divisi = data['divisi']

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
            surat = db.query(SuratMasuk).filter(SuratMasuk.id == surat_id).first()
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
            surat = db.query(SuratMasuk).filter(SuratMasuk.id == surat_id).first()
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
surat_masuk_service = SuratMasukService() 