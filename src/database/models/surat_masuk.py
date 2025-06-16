from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database.config import Base

class SuratMasuk(Base):
    __tablename__ = "surat_masuk"

    id = Column(Integer, primary_key=True, index=True)
    nomor_surat = Column(String, nullable=False)
    tanggal_surat = Column(DateTime, nullable=False)
    tanggal_terima = Column(DateTime, nullable=False)
    perihal = Column(String, nullable=False)
    pengirim = Column(String, nullable=False)
    ditujukan_kepada = Column(String, nullable=False)
    keterangan = Column(String, nullable=True)
    file_path = Column(String, nullable=False)
    inserted_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    inserted_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    array_id_dibaca_oleh = Column(ARRAY(Integer), nullable=True)

    inserted_by = relationship("User", foreign_keys=[inserted_by_id])
    dibaca_oleh = relationship("User", foreign_keys=[array_id_dibaca_oleh]) 