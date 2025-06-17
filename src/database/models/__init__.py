from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database.config import Base
import enum
from sqlalchemy import ARRAY

class RoleEnum(str, enum.Enum):
    sekertaris = "sekertaris"
    kasub = "kasub"
    staf = "staf"

class DivisiEnum(str, enum.Enum):
    teknis_dan_hukum = "teknis_dan_hukum"
    data_dan_informasi = "data_dan_informasi"
    logistik_dan_keuangan = "logistik_dan_keuangan"
    sdm_dan_parmas = "sdm_dan_parmas"

# Association tables for many-to-many relationships
surat_masuk_dibaca_oleh = Table(
    'surat_masuk_dibaca_oleh',
    Base.metadata,
    Column('surat_masuk_id', Integer, ForeignKey('surat_masuk.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)

surat_keluar_dibaca_oleh = Table(
    'surat_keluar_dibaca_oleh',
    Base.metadata,
    Column('surat_keluar_id', Integer, ForeignKey('surat_keluar.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    nama_lengkap = Column(String, nullable=False)
    role = Column(Enum(RoleEnum))
    divisi = Column(Enum(DivisiEnum), nullable=True)

    # Relationships
    surat_masuk_dibaca = relationship("SuratMasuk", secondary=surat_masuk_dibaca_oleh, back_populates="dibaca_oleh")
    surat_keluar_dibaca = relationship("SuratKeluar", secondary=surat_keluar_dibaca_oleh, back_populates="dibaca_oleh")

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
    inserted_at = Column(DateTime, nullable=False)
    inserted_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    inserted_by = relationship("User", foreign_keys=[inserted_by_id], backref="surat_masuk_inserted")
    dibaca_oleh = relationship("User", secondary=surat_masuk_dibaca_oleh, back_populates="surat_masuk_dibaca")

class SuratKeluar(Base):
    __tablename__ = "surat_keluar"

    id = Column(Integer, primary_key=True, index=True)
    nomor_surat = Column(String, nullable=False)
    tanggal_surat = Column(DateTime, nullable=False)
    tanggal_kirim = Column(DateTime, nullable=False)
    ditujukan_kepada = Column(String, nullable=False)
    perihal = Column(String, nullable=False)
    keterangan = Column(String)
    file_path = Column(String, nullable=False)
    inserted_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    inserted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    inserted_by = relationship("User", foreign_keys=[inserted_by_id], backref="surat_keluar_inserted")
    dibaca_oleh = relationship("User", secondary=surat_keluar_dibaca_oleh, back_populates="surat_keluar_dibaca") 

class TemplateSurat(Base):
    __tablename__ = "template_surat"
    id = Column(Integer, primary_key=True, index=True)
    nama_template = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    inserted_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    inserted_at = Column(DateTime, default=datetime.utcnow)
    





