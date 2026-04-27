from flask import Flask, request, render_template, redirect, url_for, jsonify
from database import DatabaseManager, WeatherObservation
import requests

app = Flask(__name__)
db = DatabaseManager()

def get_weather_data(city, country):
    try:
        # 1. Geocoding API
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        res = requests.get(geo_url, params={"name": city, "count": 1})
        if res.status_code != 200:
            return None
        
        res_data = res.json()
        if "results" not in res_data or not res_data["results"]:
            return None
        geo = res_data["results"][0]

        # 2. Weather API
        weather_url = "https://api.open-meteo.com/v1/forecast"
        w_res = requests.get(weather_url, params={
            "latitude": geo['latitude'],
            "longitude": geo['longitude'],
            "current_weather": "true"
        })
        if w_res.status_code != 200:
            return None
        
        w_data = w_res.json()
        current = w_data["current_weather"]

        return {
            "city": city,
            "country": country,
            "latitude": geo['latitude'],
            "longitude": geo['longitude'],
            "temperature_c": current['temperature'],
            "windspeed_kmh": current['windspeed'],
            "observation_time": current['time']
        }
    except Exception as e:
        print(f"External API Error: {e}")
        return None

# HTML View (Dashboard)
@app.route("/", methods=["GET"])
def index():
    observations = WeatherObservation.all(db)
    return render_template("index.html", observations=observations)

# API Endpoints
# 1. Create - Ingest Weather
@app.route("/ingest", methods=["POST"])
def ingest():
    # Query parameter(?city=)
    # Form data(HTML) 
    city = request.args.get("city") or request.form.get("city")
    country = request.args.get("country") or request.form.get("country")
    
    if not city or not country:
        return jsonify({"error": "Missing city or country"}), 400
        
    data = get_weather_data(city, country)
    if not data:
        return jsonify({"error": "Failed to fetch weather data"}), 400
        
    obs = WeatherObservation(db, **data)
    obs.save()
    
    # HTML -> redirect
    # API -> JSON
    if request.form:
        return redirect(url_for("index"))
    
    result = {k: v for k, v in vars(obs).items() if k != 'db'}
    return jsonify(result), 200

# 2. Read - List all observations (GET /observations)
@app.route("/observations", methods=["GET"])
def get_all():
    obs_list = WeatherObservation.all(db)
    results = [{k: v for k, v in vars(o).items() if k != 'db'} for o in obs_list]
    return jsonify(results), 200

# 3. Read - Retrieve by ID (GET /observations/{id})
@app.route("/observations/<int:id>", methods=["GET"])
def get_one(id):
    obs = WeatherObservation.get_by_id(db, id)
    if not obs:
        return jsonify({"error": "Not found"}), 404
    return jsonify({k: v for k, v in vars(obs).items() if k != 'db'}), 200

# 4. Update - Modify notes field (PUT /observations/{id})
# HTML (POST)
# API (PUT) 
@app.route("/observations/<int:id>", methods=["PUT", "POST"])
def update_observation(id):
    obs = WeatherObservation.get_by_id(db, id)
    if not obs:
        return jsonify({"error": "Not found"}), 404
        
    if request.method == "PUT":
        # API JSON 
        data = request.get_json()
        notes = data.get("notes")
    else:
        # HTML
        notes = request.form.get("notes")
        
    obs.update_notes(notes)
    
    if request.method == "PUT":
        return jsonify({"id": id, "notes": notes}), 200
    return redirect(url_for("index"))

# 5. Delete - Remove observation (DELETE /observations/{id})
@app.route("/observations/<int:id>", methods=["DELETE"])
def delete_observation(id):
    obs = WeatherObservation.get_by_id(db, id)
    if not obs:
        return jsonify({"error": "Not found"}), 404
    obs.delete()
    return jsonify({"deleted": id}), 200

# HTML 삭제 (POST /observations/delete/{id})
@app.route("/observations/delete/<int:id>", methods=["POST"])
def delete_form(id):
    obs = WeatherObservation.get_by_id(db, id)
    if obs:
        obs.delete()
    return redirect(url_for("index"))
