from src.database.config import SessionLocal
from src.database.models import User, SuratMasuk, SuratKeluar
from sqlalchemy.orm import joinedload
from sqlalchemy import or_

class NotificationService:
    def get_unread_notifications(self, user_id):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return [], "User not found"

            notifications = []
            
            # 1. Ambil Surat Masuk yang belum dibaca
            surat_masuk_query = db.query(SuratMasuk).options(
                joinedload(SuratMasuk.inserted_by)
            )
            # Filter berdasarkan divisi user (sekertaris bisa melihat semua)
            if user.role != 'sekertaris':
                surat_masuk_query = surat_masuk_query.filter(SuratMasuk.divisi == user.divisi)
            all_surat_masuk = surat_masuk_query.order_by(SuratMasuk.inserted_at.desc()).all()

            for surat in all_surat_masuk:
                if surat.dibaca_oleh_id is None or user.id not in surat.dibaca_oleh_id:
                    notifications.append({
                        "id": f"sm-{surat.id}",
                        "type": "surat_masuk",
                        "surat_id": surat.id,
                        "title": "Surat Masuk Baru",
                        "message": f"Surat dari {surat.pengirim} perihal '{surat.perihal}' telah diterima.",
                        "date": surat.inserted_at.strftime('%Y-%m-%d %H:%M:%S'),
                        "is_read": False,
                        "divisi": surat.divisi
                    })
            
            # 2. Ambil Surat Keluar yang belum dibaca
            surat_keluar_query = db.query(SuratKeluar).options(
                joinedload(SuratKeluar.inserted_by)
            )
            # Filter berdasarkan divisi user (sekertaris bisa melihat semua)
            if user.role != 'sekertaris':
                surat_keluar_query = surat_keluar_query.filter(SuratKeluar.divisi == user.divisi)
            all_surat_keluar = surat_keluar_query.order_by(SuratKeluar.inserted_at.desc()).all()

            for surat in all_surat_keluar:
                if surat.dibaca_oleh_id is None or user.id not in surat.dibaca_oleh_id:
                    notifications.append({
                        "id": f"sk-{surat.id}",
                        "type": "surat_keluar",
                        "surat_id": surat.id,
                        "title": "Surat Keluar Baru",
                        "message": f"Surat untuk {surat.ditujukan_kepada} perihal '{surat.perihal}' telah dibuat.",
                        "date": surat.inserted_at.strftime('%Y-%m-%d %H:%M:%S'),
                        "is_read": False,
                        "divisi": surat.divisi
                    })

            # Urutkan semua notifikasi berdasarkan tanggal, dari yang terbaru
            notifications.sort(key=lambda x: x['date'], reverse=True)

            return notifications, None

        finally:
            db.close()

# Create a singleton instance
notification_service = NotificationService() 