from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, BigInteger, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import os
from dotenv import load_dotenv

load_dotenv()

# データベース接続文字列の取得
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://fusr:ffffuuuu@localhost:5432/fldb"
)

# エンジンとセッションの設定
engine = create_engine(DATABASE_URL, echo=True)  # デバッグのためechoをTrueに
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Baseの作成
Base = declarative_base()

class Folder(Base):
    __tablename__ = "folders"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey('folders.id', ondelete='CASCADE'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # SQLAlchemy の関係性を定義
    parent = relationship("Folder", remote_side=[id], back_populates="children")
    children = relationship("Folder", back_populates="parent", cascade="all, delete-orphan")
    files = relationship("FileVersion", back_populates="folder", cascade="all, delete-orphan")

class FileVersion(Base):
    __tablename__ = "file_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False, index=True)
    version = Column(Integer, nullable=False)
    file_path = Column(String, nullable=False)
    folder_id = Column(Integer, ForeignKey('folders.id', ondelete='SET NULL'), nullable=True)
    memo = Column(Text)
    operation = Column(String, nullable=False)  # 'create', 'update', 'delete'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    file_size = Column(BigInteger)
    mime_type = Column(String)
    
    # SQLAlchemy の関係性を定義
    folder = relationship("Folder", back_populates="files")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """データベーステーブルを作成"""
    Base.metadata.create_all(bind=engine)