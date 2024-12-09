from app import db
from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

class Countries(db.Model):
    __tablename__ = 'Tari'
    id = mapped_column(Integer, primary_key=True)
    nume_tara = mapped_column(String, unique=True, nullable=False)
    latitudine = mapped_column(Float)
    longitudine = mapped_column(Float)