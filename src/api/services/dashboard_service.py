from sqlalchemy import func
from src.database.config import SessionLocal
from src.database.models import SuratMasuk, SuratKeluar, User, TemplateSurat

class DashboardService:
    def __init__(self):
        pass

    def get_stats(self):
        db = SessionLocal()

        try:
            # Get total surat masuk
            total_surat_masuk = db.query(SuratMasuk).count()

            # Get total surat keluar
            total_surat_keluar = db.query(SuratKeluar).count()

            # Get total anggota (users)
            total_anggota = db.query(User).count()

            # Get total template surat
            total_template = db.query(TemplateSurat).count()

            return {
                'total_surat_masuk': total_surat_masuk,
                'total_surat_keluar': total_surat_keluar,
                'total_anggota': total_anggota,
                'total_template': total_template
            }
        finally:
            db.close()
        