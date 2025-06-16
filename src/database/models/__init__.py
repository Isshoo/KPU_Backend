from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database.config import Base
import enum


class RoleEnum(str, enum.Enum):
    sekertaris = "sekertaris"
    kasub = "kasub"
    staf = "staf"

class DivisiEnum(str, enum.Enum):
    teknis_dan_hukum = "teknis_dan_hukum"
    data_dan_informasi = "data_dan_informasi"
    logistik_dan_keuangan = "logistik_dan_keuangan"
    sdm_dan_parmas = "sdm_dan_parmas"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    nama_lengkap = Column(String, nullable=False)
    role = Column(Enum(RoleEnum))
    divisi = Column(Enum(DivisiEnum), nullable=True)


class SuratMasuk(Base):
    __tablename__ = "surat_masuk"
    
    id = Column(Integer, primary_key=True, index=True)
    nomor_surat = Column(String, nullable=False)
    tanggal_surat_diterima = Column(DateTime, nullable=False)
    perihal = Column(String, nullable=False)
    ditujukan_kepada = Column(String, nullable=False)
    keterangan = Column(String, nullable=True)
    file_path = Column(String, nullable=False)
    inserted_at = Column(DateTime, nullable=False)
    
class SuratKeluar(Base):
    __tablename__ = "surat_keluar"
    
    id = Column(Integer, primary_key=True, index=True)
    nomor_surat = Column(String, nullable=False)
    tanggal_surat_keluar = Column(DateTime, nullable=False)
    perihal = Column(String, nullable=False)
    ditujukan_kepada = Column(String, nullable=False)
    keterangan = Column(String, nullable=True)
    file_path = Column(String, nullable=False)
    inserted_at = Column(DateTime, nullable=False)





