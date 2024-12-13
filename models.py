from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Double, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, mapped_column, DeclarativeBase
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Country(db.Model):
    __tablename__ = 'Tari'
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    nume_tara = mapped_column(String, unique=True, nullable=False)
    latitudine = mapped_column(Double)
    longitudine = mapped_column(Double)
    
    cities = relationship('City', backref='country', cascade='all, delete') 

class City(db.Model):
    __tablename__ = 'Orase'
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_tara = mapped_column(Integer, ForeignKey('Tari.id'), nullable=False)
    nume_oras = mapped_column(String, nullable=False)
    latitudine = mapped_column(Double)
    longitudine = mapped_column(Double)

    __table_args__ = (UniqueConstraint('id_tara', 'nume_oras', name='uc_id_tara_nume_oras'),)
    temperatures = relationship('Temperature', backref='city', cascade='all, delete')

class Temperature(db.Model):
    __tablename__ = 'Temperaturi'
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    valoare = mapped_column(Double)
    timestamp = mapped_column(DateTime, default=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], unique=True)
    id_oras = mapped_column(Integer, ForeignKey('Orase.id'), nullable=False)

    __table_args__ = (UniqueConstraint('id_oras', 'timestamp', name='uc_id_oras_timestamp'),)