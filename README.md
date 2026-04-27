# Juyeon Lee's Weather Tracker 🌤

A Python application that fetches real-time weather data from the Open-Meteo API and stores weather observations in a PostgreSQL database using an ORM-based pattern. Built for **CSIS 1230 - Programming for Everyone II**.

## Features

- **Live Weather**: Fetches real-time data using the Open-Meteo API.
- **Geocoding**: Converts city and country names into coordinates automatically.
- **Data Persistence**: Stores weather observations securely in a PostgreSQL database.
- **ORM Pattern**: Follows object-oriented principles for database interaction.
- **RESTful API**: Includes endpoints for creating, reading, and deleting weather records.

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL
- Git

### Steps
1. **Clone this repository:**
   ```bash
   git clone https://github.com/juyeonode/web_project.git
   cd web_project
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your environment:**
   Create a `.env` file in the root directory and configure your database credentials:
   ```plaintext
   DB_NAME=your_db_name
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

4. **Initialize the database:**
   Ensure your PostgreSQL server is running and the database specified in `.env` is created.

## Usage
Run the application using the following command:

```bash
python main.py
```

Once running, navigate to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to test the API endpoints directly using the Swagger UI interface.

## Example API Request
To ingest weather data for a specific city:

```bash
POST /ingest?city=Seoul&country=South%20Korea
```

## Project Structure

```text
web_project/
├── main.py             # FastAPI application and routes
├── database.py         # Database manager and ORM models
├── templates/          # HTML templates for the web interface
├── requirements.txt    # Project dependencies
├── .env                # Environment configuration (Hidden)
└── README.md           # Documentation
```

## Technologies Used
- Python 3
- FastAPI
- PostgreSQL
- Psycopg (Database adapter)
- Open-Meteo API
- Requests (HTTP library)