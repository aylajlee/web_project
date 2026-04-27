import requests
from flask import Flask, request, jsonify, render_template
from database import DatabaseManager, WeatherObservation

app = Flask(__name__)
db = DatabaseManager()

def get_weather_data(city, country):
    # Geocoding: 도시명, 국가명으로 위도, 경도를 찾음 
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_resp = requests.get(
        geo_url, 
        params={"name": city, "country": country, "count": 1}
    )
    
    # 응답 실패 error handling
    if not geo_resp.ok or "results" not in geo_resp.json(): 
        return None
    
    # 검색 결과 중 첫 번째 위치 정보 
    geo = geo_resp.json()["results"][0]
    
    # Weather: 위도, 경도를 이용해 현재 날씨 API 호출 
    weather_url = "https://api.open-meteo.com/v1/forecast?current_weather=true"
    weather_resp = requests.get(
        weather_url, 
        params={"latitude": geo['latitude'], 
                "longitude": geo['longitude'], 
                "current_weather": True}
    )
    
    # 날씨 API 실패 시 None 반환 
    if not weather_resp.ok: 
        return None
    
    # DB 저장
    data = weather_resp.json()
    return {
        "city": city, "country": country, "latitude": geo['latitude'], "longitude": geo['longitude'],
        "temperature": data['current_weather']['temperature'], "elevation": data['elevation'],
        "windspeed": data['current_weather']['windspeed'], "observation_time": data['current_weather']['time']
    }

@app.route("/", methods=["GET"])
def read_root():
    return render_template("index.html")


# POST /ingest
# 외부날씨데이터를 가져와서 DB에 저장 
@app.route("/ingest", methods=["POST"])
def ingest():
    city = request.args.get("city")
    country = request.args.get("country")
    data = get_weather_data(city, country)
    
    # 데이터가 없으면 400 Bad request 반환 
    if not data: 
        return jsonify({"error": "Data not found"}), 400
        
    # ORM 생성 및 저장
    obs = WeatherObservation(db, **data)
    obs.save()
    return jsonify({"id": obs.id, **data}), 200

# 전체 데이터 조회 
@app.route("/observations", methods=["GET"])
def get_all():
    obs_list = WeatherObservation.all(db)
    # db 객체 빼고 
    results = [{k: v for k, v in vars(o).items() if k != 'db'} for o in obs_list]
    return jsonify(results)

# 특정id 데이터 조회 
@app.route("/observations/<int:id>", methods=["GET"])
def get_one(id):
    obs = WeatherObservation.find_by_id(db, id)
    if not obs: 
        return jsonify({"error": "Not found"}), 404
    # db 객체 빼고 
    return jsonify({k: v for k, v in vars(obs).items() if k != 'db'})

# id의 notes 수정 
@app.route("/observations/<int:id>", methods=["PUT"])
def update_note(id):
    data = request.get_json()
    notes = data.get("notes")
    
    obs = WeatherObservation.find_by_id(db, id)
    if not obs: 
        return jsonify({"error": "Not found"}), 404
        
    obs.notes = notes
    obs.save()
    return jsonify({"id": id, "notes": notes})

# id 데이터 삭제 
@app.route("/observations/<int:id>", methods=["DELETE"])
def delete_obs(id):
    obs = WeatherObservation.find_by_id(db, id)
    if not obs: 
        return jsonify({"error": "Not found"}), 404
    obs.delete()
    return jsonify({"deleted": id})

# 서버 실행 
if __name__ == "__main__":
    app.run(debug=True, port=8000)