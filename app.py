from flask import Flask, request, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship
from sqlalchemy import Integer, String, Double, DateTime, ForeignKey, UniqueConstraint
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
    timestamp = mapped_column(DateTime, default=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
    id_oras = mapped_column(Integer, ForeignKey('Orase.id'), nullable=False)

    __table_args__ = (UniqueConstraint('id_oras', 'timestamp', name='uc_id_oras_timestamp'),)

with app.app_context():
    db.create_all()
    print('Tables created')


def check_fields_validity(required_fields_arr, payload):
    for field in required_fields_arr:
        if field not in payload:
            return False, field
        
    return True, None

def check_fields_type_validity(expected_types, payload):
    for field, expected_type in expected_types.items():
        if not isinstance(payload[field], expected_type):
            return False, field, expected_type 
        
    return True, None, None

@app.route('/api/countries', methods = ['POST'])
def add_country():
    payload = request.json
    required_fields = ['nume', 'lat', 'lon']
    required_types = {'nume': str, 'lat': float, 'lon': float}

    valid_fields, missing_field = check_fields_validity(required_fields, payload)

    if not valid_fields:
            return jsonify({"error": "Field `{}` doesn't exist".format(missing_field)}), 400
        
    valid_types, invalid_field, expected_type = check_fields_type_validity(required_types, payload)
    if not valid_types:
        return jsonify({"error": "Field `{}` should be of type {}".format(invalid_field, expected_type)}), 400

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
    required_fields = ['id', 'nume', 'lat', 'lon']
    required_types = {'id': int, 'nume': str, 'lat': float, 'lon': float}

    valid_fields, missing_field = check_fields_validity(required_fields, payload)

    if not valid_fields:
            return jsonify({"error": "Field `{}` doesn't exist".format(missing_field)}), 400
        
    valid_types, invalid_field, expected_type = check_fields_type_validity(required_types, payload)
    if not valid_types:
        return jsonify({"error": "Field `{}` should be of type {}".format(invalid_field, expected_type)}), 400
    
    
    if id != payload['id']:
        return jsonify({"error" : "The ID inside the URL and the ID inside the payload should match"}), 400

    country_to_update = Country.query.filter_by(id = payload['id']).scalar()
    if not country_to_update:
        return jsonify({"error": "ID {} doesn't exist".format(id)}), 404
        
    country_same_name = Country.query.filter(Country.id != payload['id']).filter(Country.nume_tara == payload['nume']).scalar()
    if country_same_name:
        return jsonify({"error": "Country name already exists"}), 400

    country_to_update.nume_tara = payload['nume']
    country_to_update.latitudine = payload['lat']
    country_to_update.longitudine = payload['lon']

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "DB constraints violated"}), 400

    return Response(status=200)

@app.route('/api/countries/<int:id>', methods = ['DELETE'])
def delete_country(id):
    # TODO: DELETE CASCADE FROM TEMPS
    if request.data:
        return Response(status=400)
        
    country = Country.query.filter_by(id = id).scalar()
    if not country:
        return jsonify({"error": "Provided ID was not found"}), 404

    db.session.delete(country)
    db.session.commit()

    return Response(status=200)

@app.route('/api/cities', methods = ['POST'])
def add_city():
    payload = request.json
    required_fields = ['idTara', 'nume', 'lat', 'lon']
    required_types = {'idTara': int, 'nume': str, 'lat': float, 'lon': float}

    valid_fields, missing_field = check_fields_validity(required_fields, payload)

    if not valid_fields:
            return jsonify({"error": "Field `{}` doesn't exist".format(missing_field)}), 400
        
    valid_types, invalid_field, expected_type = check_fields_type_validity(required_types, payload)
    if not valid_types:
        return jsonify({"error": "Field `{}` should be of type {}".format(invalid_field, expected_type)}), 400

    if not Country.query.filter_by(id = payload['idTara']).scalar():
        return jsonify({"error": "The ID provided doesn't match any country"}), 404

    new_city = City(id_tara = payload['idTara'], nume_oras = payload['nume'], 
                    latitudine = payload['lat'], longitudine = payload['lon'])

    db.session.add(new_city)
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "City {} already exists for country ID {}".format(payload['nume'], payload['idTara'])}), 409

    return jsonify({"id": new_city.id}), 201


@app.route('/api/cities', methods = ['GET'])
def get_cities():
    cities = City.query.all()

    cities_arr = [{"id": city.id, "idTara": city.id_tara, "nume": city.nume_oras, "lat": city.latitudine, "lon": city.longitudine}
                     for city in cities]
    
    return jsonify(cities_arr), 200


@app.route('/api/cities/country/<int:id_tara>', methods = ['GET'])
def get_cities_by_country(id_tara):
    cities_by_country_id = City.query.filter_by(id_tara = id_tara).all()

    filtered_cities = [{"id": city.id, "idTara": city.id_tara, "nume": city.nume_oras, "lat": city.latitudine, "lon": city.longitudine}
                     for city in cities_by_country_id]
    
    return jsonify(filtered_cities), 200

@app.route('/api/cities/<int:id>', methods = ['PUT'])
def update_city(id):
    payload = request.json
    required_fields = ['id', 'idTara', 'nume', 'lat', 'lon']
    required_types = {'id': int, 'idTara': int, 'nume': str, 'lat': float, 'lon': float}

    valid_fields, missing_field = check_fields_validity(required_fields, payload)

    if not valid_fields:
            return jsonify({"error": "Field `{}` doesn't exist".format(missing_field)}), 400
        
    valid_types, invalid_field, expected_type = check_fields_type_validity(required_types, payload)
    if not valid_types:
        return jsonify({"error": "Field `{}` should be of type {}".format(invalid_field, expected_type)}), 400

    if id != payload['id']:
        return jsonify({"error": "The ID inside the URL and the ID inside the payload should match"}), 400
    
    city_to_update = City.query.filter_by(id = id).scalar()
    if not city_to_update:
        return jsonify({"error": "The provided ID doesn't match any city"}), 404
    
    if not Country.query.filter_by(id = payload['idTara']).scalar():
        return jsonify({"error": "The provided country ID doesn't match any country"}), 404
    
    if City.query.filter(City.id != payload['id']).filter(City.id_tara == payload['idTara']).filter(City.nume_oras == payload['nume']).scalar():
        return jsonify({"error": "Provided city name already exists for provided country ID"}), 409
    
    city_to_update.id_tara = payload['idTara']
    city_to_update.nume_oras = payload['nume']
    city_to_update.latitudine = payload['lat']
    city_to_update.longitudine = payload['lon']

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "DB constraints violated"}), 400
    
    return Response(status=200)

@app.route('/api/cities/<int:id>', methods = ['DELETE'])
def delete_city(id):
    if request.data:
        return Response(status=400)
        
    city = City.query.filter_by(id = id).scalar()
    if not city:
        return jsonify({"error": "Provided ID was not found"}), 404

    db.session.delete(city)
    db.session.commit()

    return Response(status=200)

@app.route('/api/temperatures', methods = ['POST'])
def add_temperature():
    # TODO: ret 409 for same city id and timestamp
    payload = request.json
    required_fields = ["id_oras", "valoare"]
    required_types = {"id_oras": int, "valoare": float}

    valid_fields, missing_field = check_fields_validity(required_fields, payload)

    if not valid_fields:
            return jsonify({"error": "Field `{}` doesn't exist".format(missing_field)}), 400
        
    valid_types, invalid_field, expected_type = check_fields_type_validity(required_types, payload)
    if not valid_types:
        return jsonify({"error": "Field `{}` should be of type {}".format(invalid_field, expected_type)}), 400

    if not City.query.filter_by(id = payload['id_oras']).scalar():
        return jsonify({"error": "Provided city ID doesn't match any city"}), 404

    new_temperature = Temperature(valoare = payload['valoare'], id_oras = payload['id_oras'])
    db.session.add(new_temperature)
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "DB constraints violated"}), 400
    
    return jsonify({"id": new_temperature.id}), 201

if __name__ == '__main__':
    app.run(debug=True)
