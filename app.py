from flask import Flask, request, Response, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from datetime import datetime, timezone
from os import environ
from models import db, Country, City, Temperature

db_user = environ.get('DATABASE_USER')
db_pass = environ.get('DATABASE_PASSWORD')
db_name = environ.get('DATABASE_NAME')
db_url = environ.get('DATABASE_URL')
db_port = environ.get('DATABASE_PORT')

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{db_user}:{db_pass}@{db_url}:{db_port}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

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

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

@app.route('/api/countries', methods = ['POST'])
def add_country():
    if request.is_json:
        payload = request.json
    else:
        return jsonify({"error": "Request should be of type JSON"}), 400

    required_fields = ['nume', 'lat', 'lon']
    required_types = {'nume': str, 'lat': float, 'lon': float}

    valid_fields, missing_field = check_fields_validity(required_fields, payload)

    if not valid_fields:
            return jsonify({"error": "Field `{}` doesn't exist".format(missing_field)}), 400
        
    valid_types, invalid_field, expected_type = check_fields_type_validity(required_types, payload)
    if not valid_types:
        return jsonify({"error": "Field `{}` should be of type {}".format(invalid_field, expected_type)}), 400

    if Country.query.filter_by(nume_tara = payload['nume']).scalar():
        return jsonify({"error": "Country name already exists"}), 409

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
    if request.is_json:
        payload = request.json
    else:
        return jsonify({"error": "Request should be of type JSON"}), 400

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
    if request.is_json:
        payload = request.json
    else:
        return jsonify({"error": "Request should be of type JSON"}), 400

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
    if request.is_json:
        payload = request.json
    else:
        return jsonify({"error": "Request should be of type JSON"}), 400

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
        return Response(status=404)

    db.session.delete(city)
    db.session.commit()

    return Response(status=200)

@app.route('/api/temperatures', methods = ['POST'])
def add_temperature():
    if request.is_json:
        payload = request.json
    else:
        return jsonify({"error": "Request should be of type JSON"}), 400

    required_fields = ["idOras", "valoare"]
    required_types = {"idOras": int, "valoare": float}

    valid_fields, missing_field = check_fields_validity(required_fields, payload)

    if not valid_fields:
            return jsonify({"error": "Field `{}` doesn't exist".format(missing_field)}), 400
        
    valid_types, invalid_field, expected_type = check_fields_type_validity(required_types, payload)
    if not valid_types:
        return jsonify({"error": "Field `{}` should be of type {}".format(invalid_field, expected_type)}), 400

    if not City.query.filter_by(id = payload['idOras']).scalar():
        return jsonify({"error": "Provided city ID doesn't match any city"}), 404

    new_temperature = Temperature(valoare = payload['valoare'], id_oras = payload['idOras'], timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])

    if Temperature.query.filter(Temperature.id_oras == payload['idOras']).filter_by(timestamp = new_temperature.timestamp).scalar(): 
        return jsonify({"error": "Same city ID and timestamp are not allowed"}), 409
    
    db.session.add(new_temperature)
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "DB constraints violated"}), 409
    
    return jsonify({"id": new_temperature.id}), 201


@app.route('/api/temperatures', methods = ['GET'])
def get_temperatures():
    try:
        lat = request.args.get('lat', type=float)
    except ValueError:
        return jsonify({"error": "Latitude should be a float"}), 400

    try:
        lon = request.args.get('lon', type=float)
    except ValueError:
        return jsonify({"error": "Longitude should be a float"}), 400


    from_date = request.args.get('from')
    until_date = request.args.get('until')

    if from_date: 
        if is_valid_date(from_date):
            from_date = datetime.strptime(from_date, "%Y-%m-%d")
        else:
            return jsonify({"error": "Invalid date format. Should be YYYY-MM-DD"}), 400

    if until_date: 
        if is_valid_date(until_date):
            until_date = datetime.strptime(until_date, "%Y-%m-%d")
        else:
            return jsonify({"error": "Invalid date format. Should be YYYY-MM-DD"}), 400


    filtered_temperatures = None

    if lat:
        filtered_temperatures = Temperature.query.filter(Temperature.city.has(latitudine=lat))
    
    if lon:
        if filtered_temperatures:
            filtered_temperatures = filtered_temperatures.filter(Temperature.city.has(longitudine=lon))
        else:
            filtered_temperatures = Temperature.query.filter(Temperature.city.has(longitudine=lon))

    if from_date:
        if filtered_temperatures:
            filtered_temperatures = filtered_temperatures.filter(func.date(Temperature.timestamp) >= from_date)
        else:
            filtered_temperatures = Temperature.query.filter(func.date(Temperature.timestamp) >= from_date)

    if until_date:
        if filtered_temperatures:
            filtered_temperatures = filtered_temperatures.filter(func.date(Temperature.timestamp) <= until_date)
        else:
            filtered_temperatures = Temperature.query.filter(func.date(Temperature.timestamp) <= until_date)

    if not filtered_temperatures:
        filtered_temperatures = Temperature.query.all()
    else:
        filtered_temperatures = filtered_temperatures.all()

    filtered_temps_arr = [{"id": temp.id, "valoare": temp.valoare, "timestamp": temp.timestamp} for temp in filtered_temperatures]
    
    return jsonify(filtered_temps_arr), 200
    
@app.route('/api/temperatures/cities/<int:id_oras>', methods = ['GET'])
def get_temperatures_by_city(id_oras):
    from_date = request.args.get('from')
    until_date = request.args.get('until')

    if from_date: 
        if is_valid_date(from_date):
            from_date = datetime.strptime(from_date, "%Y-%m-%d")
        else:
            return jsonify({"error": "Invalid date format. Should be YYYY-MM-DD"}), 400

    if until_date: 
        if is_valid_date(until_date):
            until_date = datetime.strptime(until_date, "%Y-%m-%d")
        else:
            return jsonify({"error": "Invalid date format. Should be YYYY-MM-DD"}), 400

    filtered_temperatures = Temperature.query.filter_by(id_oras = id_oras)

    if from_date:
        filtered_temperatures = filtered_temperatures.filter(func.date(Temperature.timestamp) >= from_date)
    
    if until_date:
        filtered_temperatures = filtered_temperatures.filter(func.date(Temperature.timestamp) <= until_date)

    filtered_temps_arr = [{"id": temp.id, "valoare": temp.valoare, "timestamp": temp.timestamp} for temp in filtered_temperatures]

    return jsonify(filtered_temps_arr), 200

@app.route('/api/temperatures/countries/<int:id_tara>', methods = ['GET'])
def get_temperatures_by_country(id_tara):
    from_date = request.args.get('from')
    until_date = request.args.get('until')

    if from_date: 
        if is_valid_date(from_date):
            from_date = datetime.strptime(from_date, "%Y-%m-%d")
        else:
            return jsonify({"error": "Invalid date format. Should be YYYY-MM-DD"}), 400

    if until_date: 
        if is_valid_date(until_date):
            until_date = datetime.strptime(until_date, "%Y-%m-%d")
        else:
            return jsonify({"error": "Invalid date format. Should be YYYY-MM-DD"}), 400

    filtered_temperatures = Temperature.query.filter(Temperature.city.has(id_tara = id_tara))

    if from_date:
        filtered_temperatures = filtered_temperatures.filter(func.date(Temperature.timestamp) >= from_date)
    
    if until_date:
        filtered_temperatures = filtered_temperatures.filter(func.date(Temperature.timestamp) <= until_date)

    filtered_temps_arr = [{"id": temp.id, "valoare": temp.valoare, "timestamp": temp.timestamp} for temp in filtered_temperatures]

    return jsonify(filtered_temps_arr), 200

@app.route('/api/temperatures/<int:id>', methods = ['PUT'])
def update_temperature(id):
    if request.is_json:
        payload = request.json
    else:
        return jsonify({"error": "Request should be of type JSON"}), 400

    required_fields = ["id", "idOras", "valoare"]
    required_types = {"id": int, "idOras": int, "valoare": float}

    valid_fields, missing_field = check_fields_validity(required_fields, payload)

    if not valid_fields:
        return jsonify({"error": "Field `{}` doesn't exist".format(missing_field)}), 400
    
    valid_types, invalid_field, expected_type = check_fields_type_validity(required_types, payload)

    if not valid_types:
        return jsonify({"error": "Field `{}` should be of type {}".format(invalid_field, expected_type)}), 400
    
    if id != payload['id']:
        return jsonify({"error": "The ID inside the URL and the ID inside the payload should match"}), 400
    
    temperature_to_update = Temperature.query.filter_by(id = id).scalar()
    if not temperature_to_update:
        return jsonify({"error": "The provided ID doesn't match any temperature"}), 404
    
    temperature_to_update.valoare = payload['valoare']
    temperature_to_update.id_oras = payload['idOras']
    temperature_to_update.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    if Temperature.query.filter(Temperature.id_oras == payload['idOras']).filter_by(timestamp = temperature_to_update.timestamp).scalar():
        return jsonify({"error": "Same city ID and timestamp are not allowed"}), 409
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "DB constraints violated"}), 400
    
    return Response(status=200)


@app.route('/api/temperatures/<int:id>', methods = ['DELETE'])
def delete_temperature(id):
    if request.data:
        return Response(status=400)
    
    temperature = Temperature.query.filter_by(id = id).scalar()
    if not temperature:
        return jsonify({"error": "Provided ID was not found"}), 404
    
    db.session.delete(temperature)
    db.session.commit()
    
    return Response(status=200)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6000)
