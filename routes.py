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
        if res.status_code != 200: return None
        
        res_data = res.json()
        if "results" not in res_data or not res_data["results"]: return None
        geo = res_data["results"][0]

        # 2. Weather API
        weather_url = "https://api.open-meteo.com/v1/forecast"
        w_res = requests.get(weather_url, params={
            "latitude": geo['latitude'],
            "longitude": geo['longitude'],
            "current_weather": "true"
        })
        if w_res.status_code != 200: return None
        
        w_data = w_res.json()
        current = w_data["current_weather"]

        return {
            "city": city,
            "country": country,
            "latitude": geo['latitude'],
            "longitude": geo['longitude'],
            "temperature": current['temperature'],
            "elevation": int(geo.get('elevation', 0)),
            "windspeed": current['windspeed'],
            "observation_time": current['time']
        }
    except Exception as e:
        print(f"Internal error: {e}")
        return None

# HTML
@app.route("/", methods=["GET"])
def index():
    observations = WeatherObservation.all(db)
    return render_template("index.html", observations=observations)

@app.route("/ingest", methods=["POST"])
def ingest():
    city = request.form.get("city")
    country = request.form.get("country")
    data = get_weather_data(city, country)
    if not data: return "Failed to fetch data", 400
    
    obs = WeatherObservation(db, **data)
    obs.save()
    return redirect(url_for("index"))

# JSON API 

# 전체 조회 (GET /observations)
@app.route("/observations", methods=["GET"])
def get_all():
    obs_list = WeatherObservation.all(db)
    # db 객체 제외 
    # 딕셔너리 형태로 변환
    results = [{k: v for k, v in vars(o).items() if k != 'db'} for o in obs_list]
    return jsonify(results), 200

# 특정ID 조회 (GET /observations/<id>)
@app.route("/observations/<int:id>", methods=["GET"])
def get_one(id):
    obs = WeatherObservation.get_by_id(db, id) 
    if not obs: return jsonify({"error": "Not found"}), 404
    return jsonify({k: v for k, v in vars(obs).items() if k != 'db'}), 200

# 메모 수정 (PUT /observations/<id> - JSON )
@app.route("/observations/<int:id>", methods=["PUT"])
def update_json(id):
    data = request.get_json()
    notes = data.get("notes")
    obs = WeatherObservation.get_by_id(db, id)
    if not obs: return jsonify({"error": "Not found"}), 404
    obs.update_notes(notes)
    return jsonify({"id": id, "notes": notes}), 200

# 삭제 (DELETE /observations/<id> - JSON)
@app.route("/observations/<int:id>", methods=["DELETE"])
def delete_json(id):
    obs = WeatherObservation.get_by_id(db, id)
    if not obs: return jsonify({"error": "Not found"}), 404
    obs.delete()
    return jsonify({"deleted": id}), 200

# 기존 HTML Update/Delete
@app.route("/observations/<int:id>", methods=["POST"])
def update_form(id):
    notes = request.form.get("notes")
    obs = WeatherObservation.get_by_id(db, id)
    if obs: obs.update_notes(notes)
    return redirect(url_for("index"))

@app.route("/observations/delete/<int:id>", methods=["POST"])
def delete_form(id):
    obs = WeatherObservation.get_by_id(db, id)
    if obs: obs.delete()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, port=8000)
