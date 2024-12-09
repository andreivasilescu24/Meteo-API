from flask import Flask, request, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Integer, String, Double, DateTime, select
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

class Base(DeclarativeBase):
    pass

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://scd_student:tema2_scd@localhost:5432/scd_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app, model_class=Base)

class Country(db.Model):
    __tablename__ = 'Tari'
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    nume_tara = mapped_column(String, unique=True, nullable=False)
    latitudine = mapped_column(Double)
    longitudine = mapped_column(Double)

class City(db.Model):
    __tablename__ = 'Orase'
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_tara = mapped_column(Integer, unique=True)
    nume_oras = mapped_column(String, unique=True, nullable=False)
    latitudine = mapped_column(Double)
    longitudine = mapped_column(Double)

class Temperature(db.Model):
    __tablename__ = 'Temperaturi'
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    valoare = mapped_column(Double)
    timestamp = mapped_column(DateTime, unique=True, default=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
    id_oras = mapped_column(Integer, unique=True)

with app.app_context():
    db.create_all()
    print('Tables created')


@app.route('/api/countries', methods = ['POST'])
def add_country():
    payload = request.json
    required_field_names = ['nume', 'lat', 'lon']
    
    if not(payload):
        return jsonify({"error": "Payload is not in json format"}), 400
    
    for field in required_field_names:
        if field not in payload:
            return jsonify({"error": "Field {} doesn't exist".format(field)}), 400
        
    if not isinstance(payload['nume'], str)\
        or not isinstance(payload['lat'], float)\
        or not isinstance(payload['lon'], float):
            return jsonify({"error": "Incorrect types for fields"}), 400

    new_country = Country(nume_tara = payload['nume'], latitudine = payload['lat'], longitudine = payload['lon'])
    db.session.add(new_country)
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return Response(status=409) 
    
    return jsonify({"id": new_country.id}), 201


@app.route('/api/countries', methods = ['GET'])
def get_countries():
    countries = Country.query.all()

    countries_arr = [{"id": country.id, "nume": country.nume_tara, "lat": country.latitudine, "lon": country.longitudine}
                     for country in countries]
    
    return jsonify(countries_arr), 200


@app.route('/api/countries/<int:id>', methods = ['PUT'])
def update_country(id):
    payload = request.json
    required_field_names = ['id', 'nume', 'lat', 'lon']

    if not(payload):
        return jsonify({"error": "Payload is not in json format"}), 400
    
    for field in required_field_names:
        if field not in payload:
            return jsonify({"error": "Field {} doesn't exist".format(field)}), 400
        
    if not isinstance(payload['id'], int)\
        or not isinstance(payload['nume'], str)\
        or not isinstance(payload['lat'], float)\
        or not isinstance(payload['lon'], float):
            return jsonify({"error": "Incorrect types for fields"}), 400
    
    if db.session.query(Country).filter(Country.id == payload['id'], Country.id != id):
        return jsonify({"error": "ID already exists"}), 400
    
    if Country.query.filter(Country.nume_tara == payload['nume'], Country.id != id):
        return jsonify({"error": "Country name already exists"}), 400

    country = Country.query.get(id)
    if not country:
        return jsonify({"error": "ID {} doesn't exist".format(id)}), 404

    country.id = payload['id']
    country.nume_tara = payload['nume']
    country.latitudine = payload['lat']
    country.longitudine = payload['lon']

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "DB constraints violated"}), 400

    return Response(status=200)

@app.route('/api/countries/<int:id>', methods = ['DELETE'])
def delete_country(id):
    raise NotImplementedError



if __name__ == '__main__':
    app.run(debug=True)
