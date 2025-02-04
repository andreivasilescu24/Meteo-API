# API Flask with PostgreSQL

This project represents a Flask API created for managing metheorological values, that interacts with a PostgreSQL database. It provides endpoints for managing countries, cities, and temperatures.

## Project Structure

## Containers

Run: `docker compose up --build`

This will start the following services:

- `api`: The Flask API service running on port 6000 (accessible at `http://localhost:6000`)
- `db`: The PostgreSQL database service running on port 5432 (accessible at `http://localhost:5432`)
- `pgadmin`: The database management service running on port 8081 (accessible at `http://localhost:8081`)

Add a `.env` file to define the following environment variables:

- `DATABASE_URL`: The database URL. (`db` in order to use the Docker service)
- `DATABASE_USER`: The database user.
- `DATABASE_PASSWORD`: The database password.
- `DATABASE_NAME`: The database name.
- `DATABASE_PORT`: The database port.
- `PGADMIN_DEFAULT_EMAIL`: pgAdmin login email.
- `PGADMIN_DEFAULT_PASSWORD`: pgAdmin login password.

### Dockerfile

The `Dockerfile` is used to build the Docker image for the application. It contains instructions for installing dependencies and configuring the runtime environment for the Flask API.

Includes:

- Setting the base image (`python:latest`).
- Installing dependencies specified in `requirements.txt`.
- Copying the source code into the container (excluding unnecessary files specified in `.dockerignore`).
- Running the Flask application.

## API

### Endpoints

- `POST /api/countries`: Add a new country
- `GET /api/countries`: Retrieve all countries
- `PUT /api/countries/<int:id>`: Update a country
- `DELETE /api/countries/<int:id>`: Delete a country
- `POST /api/cities`: Add a new city
- `GET /api/cities`: Retrieve all cities
- `PUT /api/cities/<int:id>`: Update a city
- `DELETE /api/cities/<int:id>`: Delete a city
- `POST /api/temperatures`: Add a new temperature
- `GET /api/temperatures`: Retrieve temperatures

### Used Models:

The database models are defined in `models.py` using SQLAlchemy (Country, City, Temperature), corresponding to the tables created when the API container starts.
