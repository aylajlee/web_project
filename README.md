# Juyeon's Local Weather Tracker 🌤

A Python application that fetches real-time weather data from the Open-Meteo API and stores weather observations in a PostgreSQL database using an ORM-based pattern. Built for **CSIS 1230 - Programming for Everyone II**.

## Features
- **Live Weather**: Fetches real-time data using the Open-Meteo API.
- **Automatic Geocoding**: Automatically converts city names into coordinates.
- **Data Persistence**: Stores observations securely in PostgreSQL.
- **ORM-based Pattern**: Uses the `WeatherObservation` class for clean database interactions.
- **Full CRUD Interface**:
  - **Create**: Ingest new data via HTML form or API (`/ingest`).
  - **Read**: View records on the Dashboard or fetch as **JSON** via `/observations`.
  - **Update**: Modify personal notes using **PUT** or HTML forms.
  - **Delete**: Remove records using **DELETE** or the Dashboard.

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
   Create a `.env` file in the root directory:
   ```env
   DB_NAME=your_db_name
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

4. **Initialize the database:**
   Run the following SQL to create the table in your PostgreSQL tool:
   ```sql
   DROP TABLE IF EXISTS weather_observation CASCADE;

   CREATE TABLE weather_observation (
       id SERIAL PRIMARY KEY,
       city VARCHAR(100) NOT NULL,
       country VARCHAR(50) NOT NULL,
       latitude DECIMAL(10, 8) NOT NULL,
       longitude DECIMAL(11, 8) NOT NULL,
       temperature_c DECIMAL(5, 2),
       windspeed_kmh DECIMAL(5, 2),
       observation_time VARCHAR(100),
       notes TEXT
   );
   ```

## Usage
Run the application:
```bash
python main.py
```
Then open your browser and go to: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## API Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/ingest` | Fetches weather (supports Query Params `?city=...&country=...`). |
| **GET** | `/observations` | Retrieves all observations in **JSON** format. |
| **GET** | `/observations/<id>` | Retrieves a specific observation by ID in **JSON**. |
| **PUT** | `/observations/<id>` | Updates the notes field (JSON API). |
| **DELETE** | `/observations/<id>` | Deletes an observation from the database (JSON API). |

## Project Structure
```plaintext
web_project/
├── main.py          # Application entry point
├── routes.py        # Flask routing and CRUD logic
├── database.py      # Database manager and ORM models
├── templates/       # HTML templates (base.html, index.html)
├── requirements.txt # Project dependencies
└── README.md        # Project documentation
```

## Technologies Used
- **Language**: Python 3
- **Web Framework**: Flask
- **Database**: PostgreSQL
- **DB Adapter**: Psycopg 3
- **External API**: Open-Meteo (Geocoding & Weather)