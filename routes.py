from flask import Flask, request, render_template, redirect, url_for, jsonify
from database import DatabaseManager, WeatherObservation
import requests
import re 

app = Flask(__name__)
db = DatabaseManager()

def get_weather_data(city, country):
    """
    Geocoding API와 Open-Meteo API를 사용해 실시간 날씨 데이터를 가져옴
    """
    try:
        # 1. Geocoding API (역할: 도시 이름을 좌표(위도, 경도)로 변환)
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        # timeout 설정: API 서버 응답이 없을 경우 -> 서버가 멈추는 것을 방지 
        res = requests.get(geo_url, params={"name": city, "count": 1}, timeout=10)
        
        # HTTP 에러(4xx, 5xx) 발생 시 예외 
        # e.g. API 서버 자체 (500 error) # 주소가 잘못됐을 때 (404 error)
        res.raise_for_status()
        res_data = res.json()
        
        # API 연결은 성공했지만, 검색 결과가 없는 경우 
        # e.g. 없는 도시 이름을 검색한 경우 
        if "results" not in res_data or not res_data["results"]:
            return None
        
        # 가장 연관성이 높은 첫 번째 결과 선택 
        geo = res_data["results"][0]

        # 2. Weather API (역할: 좌표(위도, 경도)를 기반으로 현재 날씨 조회)
        # timeout 설정 
        weather_url = "https://api.open-meteo.com/v1/forecast"
        w_res = requests.get(weather_url, params={
            "latitude": geo['latitude'],
            "longitude": geo['longitude'],
            "current_weather": "true"
        }, timeout=10)
        
        # if w_res.status_code != 200:
        #     return None
        w_res.raise_for_status() # HTTP 에러 처리 
        
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
        # 에러 발생 시 로그 출력하고, None을 반환하여 시스템다운 방지 
        print(f"External API Error: {e}")
        return None

# HTML View (Main Dashboard) 메인 대시보드 화면 
@app.route("/", methods=["GET"])
def index():
    """
    모든 날씨 기록을 DB에서 가져와 
    Main Dashboard Page에 
    최신순으로 정렬하여 표시
    """
    observations = WeatherObservation.all(db)
    # 정렬 Sorting: 관측시간(observation_time)을 기준으로 내림차순 정렬 (최신순)
    sorted_obs = sorted(observations, key=lambda x: x.observation_time, reverse=True)
    
    return render_template("index.html", observations=sorted_obs)

# 1. Create: 데이터 수집 및 저장
@app.route("/ingest", methods=["POST"])
def ingest():
    """
    새로운 날씨 데이터를 수집하여 저장
    API 파라미터(?city=)와 HTML 폼 데이터 입력 모두 가능
    """
    city = request.args.get("city") or request.form.get("city")
    country = request.args.get("country") or request.form.get("country")
    
    # 입력 데이터 
    if not city or not country:
        return jsonify({"error": "Please provide both city and country name."}), 400
    
    # 이름 길이
    if len(city) < 2:
        return jsonify({"error": "City name is too short. Please provide a valid name."}), 400

    # 문자열: 도시 이름에 숫자나 특수문자가 포함되었는지
    if not re.match(r"^[a-zA-Z\s\-]+$", city):
        return jsonify({"error": "City name contains invalid characters. Use letters only."}), 400
        
    data = get_weather_data(city, country)
    if not data:
        return jsonify({"error": "Could not find weather data for this location."}), 400
    
    # API 응답 데이터 중 온도가 숫자인지 확인 
    if not isinstance(data.get('temperature_c'), (int, float)):
        return jsonify({"error": "Invalid temperature data received from API."}), 500

    obs = WeatherObservation(db, **data)
    obs.save()
    
    # HTML form -> dashboard로 이동 
    # API 요청 -> JSON 응답 
    if request.form:
        return redirect(url_for("index"))
    
    result = {k: v for k, v in vars(obs).items() if k != 'db'}
    return jsonify(result), 200

# 2. Read - List 전체 목록 조회
@app.route("/observations", methods=["GET"])
def get_all():
    """ DB에 저장된 모든 날씨 기록을 JSON 형태로 반환"""
    obs_list = WeatherObservation.all(db)
    results = [{k: v for k, v in vars(o).items() if k != 'db'} for o in obs_list]
    return jsonify(results), 200

# 3. Read - Retrieve by ID 특정 기록 조회 
# (GET /observations/{id})
@app.route("/observations/<int:id>", methods=["GET"])
def get_one(id):
    """ ID를 통해 특정 날씨 기록을 조회"""
    obs = WeatherObservation.get_by_id(db, id)
    if not obs:
        return jsonify({"error": "Observation not found in our database."}), 404
    return jsonify({k: v for k, v in vars(obs).items() if k != 'db'}), 200

# 4. Update - Modify notes field 메모 수정
# API (PUT) 
@app.route("/observations/<int:id>", methods=["PUT", "POST"])
def update_observation(id):
    """ 
    기존 날씨 기록의 notes 필드를 수정
    JSON API(PUT)와 HTML FORM(POST) 요청을 모두 처리
    """
    obs = WeatherObservation.get_by_id(db, id)
    if not obs:
        return jsonify({"error": "Cannot update because the record does not exist."}), 404
        
    if request.method == "PUT":
        # JSON 요청데이터가 없을 경우 {} 빈 딕셔너리로 처리 
        data = request.get_json() or {} 
        notes = data.get("notes")
    else:
        notes = request.form.get("notes")
        
    obs.update_notes(notes)
    
    if request.method == "PUT":
        return jsonify({"id": id, "notes": notes}), 200
    return redirect(url_for("index"))

# 5. Delete - Remove observation 데이터 삭제 
# (DELETE /observations/{id})
@app.route("/observations/<int:id>", methods=["DELETE"])
def delete_observation(id):
    """
    API 요청을 통해 특정 날씨 기록을 삭제
    """
    obs = WeatherObservation.get_by_id(db, id)
    if not obs:
        return jsonify({"error": "Cannot delete because the record does not exist."}), 404
    obs.delete()
    return jsonify({"deleted": id}), 200

# HTML 삭제 
@app.route("/observations/delete/<int:id>", methods=["POST"])
def delete_form(id):
    """ HTML Dashboard에서 삭제버튼 눌렀을 때 처리"""
    obs = WeatherObservation.get_by_id(db, id)
    if obs:
        obs.delete()
    return redirect(url_for("index"))
