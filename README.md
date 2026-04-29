# Juyeon's Local Weather Tracker 🌤

A Python application that fetches real-time weather data from the Open-Meteo API and manages observations in a PostgreSQL database using an ORM-based pattern. Built for **CSIS 1230 - Programming for Everyone II**.

## Key Features
- **Live Weather Ingestion**: Fetches real-time data (temperature, windspeed) using Open-Meteo API.
- **Automatic Geocoding**: Converts city names into precise latitude/longitude coordinates.
- **ORM-based Pattern**: Uses the `WeatherObservation` class to manage database interactions as objects, ensuring clean and modular code (OOP).
- **Automated Database Setup**: `main.py` automatically initializes tables and seeds sample data (Chicago, Seoul, Bern) on startup.
- **Full CRUD Interface**: Supports Create, Read, Update, and Delete via both Web UI and JSON API.
  - **Create**: Ingest new data via Dashboard (HTML) form or API (`/ingest`).
  - **Read**: View sorted records on the Web Dashboard or fetch as **JSON** via `/observations`.
  - **Update**: Modify personal notes using **PUT** or HTML forms.
  - **Delete**: Remove records using **DELETE** or the Dashboard's delete button.

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
   Create a `.env` file in the root directory and add your PostgreSQL credentials:
   ```env
   DB_NAME=weather_db
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

## Usage
Run the application:
```bash
python main.py
```
- **Automatic Setup**: The app will automatically create the `weather_observation` table and inject sample data if the database is empty.
- **Access**: Open your browser and go to: <http://127.0.0.1:8000>

---

## Manual Database Setup (Optional)
The application handles table creation automatically. However, if you wish to create the table manually for reference or debugging, use the following SQL script:

```sql
-- Manual table creation script
DROP TABLE IF EXISTS weather_observation CASCADE;

CREATE TABLE weather_observation (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(50) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    temperature_c DECIMAL(5, 2),
    windspeed_kmh DECIMAL(5, 2),
    observation_time VARCHAR(100),
    notes TEXT
);
```

---

## API Endpoints Overview


| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/` | **Web Dashboard**: View all observations (Sorted by latest). |
| **POST** | `/ingest` | Fetches weather (supports Query Params `?city=...&country=...` or Form Data). |
| **GET** | `/observations` | Retrieves all observations in **JSON** format. |
| **GET** | `/observations/<id>` | Retrieves a specific observation by ID in **JSON**. |
| **PUT/POST**| `/observations/<id>` | Updates the **notes** field (supports JSON PUT or Form POST). |
| **DELETE** | `/observations/<id>` | Deletes an observation from the database via API. |

## Project Structure
```plaintext
web_project/
├── main.py          # Application entry point & Auto-DB Initializer
├── routes.py        # Flask routing, CRUD logic, and API Integration
├── database.py      # Database manager and ORM models (WeatherObservation)
├── templates/       # HTML templates (base.html, index.html)
├── requirements.txt # Project dependencies
└── README.md        # Project documentation
```

## Technologies Used
- **Language**: Python 3.x
- **Web Framework**: Flask
- **Database**: PostgreSQL
- **DB Adapter**: Psycopg 3
- **External API**: Open-Meteo (Geocoding & Weather)