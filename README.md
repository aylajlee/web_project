# Juyeon Lee's Weather Tracker 🌤

A Python application that fetches real-time weather data from the Open-Meteo API and stores weather observations in a PostgreSQL database.

Built for CSIS 1230 - Programming for Everyone II.

## Description

This project retrieves weather data for a city and country, converts the location into latitude and longitude using the Open-Meteo geocoding API, then fetches current weather data from the Open-Meteo forecast API.

The application is organized using Python modules and follows the course material on API requests, object-oriented programming, database concepts, and documentation.

## Features

- Fetches live weather data from the Open-Meteo API.
- Uses the Open-Meteo geocoding endpoint to convert city and country names into coordinates.
- Stores weather observation data in PostgreSQL.
- Uses Python classes to represent weather observations.
- Includes safe error handling for API requests.
- Organized into separate Python files for cleaner structure.

## Installation

### Prerequisites

- Python 3
- PostgreSQL
- Git
- VS Code
- PgAdmin4

### Steps

1. Clone this repository:

```bash
git clone https://github.com/juyeonode/web_project.git
cd web_project
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create and activate your virtual environment if needed.

4. Set up your PostgreSQL database.

5. Create a `.env` file for environment variables if your project uses one.

## Usage

Run the project with:

```bash
python main.py
```

If your project uses a Flask app entry point, you can also run:

```bash
python app.py
```

## Project Structure

```text
web_project/
├── main.py
├── routes.py
├── requirements.txt
├── README.md
├── .gitignore
└── templates/
```

## Technologies Used

- Python 3
- Requests
- PostgreSQL
- PgAdmin4
- GitHub
- VS Code
- Open-Meteo API

## Notes

- Weather data is fetched from external APIs.
- PostgreSQL should be running before database-related features are used.
- Do not commit virtual environment folders or `.env` files to GitHub.

## Author

Juyeon Lee