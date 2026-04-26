from fastapi import FastAPI, HTTPException
import requests
from database import WeatherObservation

# FastAPI app 객체
app = FastAPI()

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

# POST /ingest: 외부날씨데이터를 가져와서 DB에 저장 
@app.post("/ingest")
def ingest(city: str, country: str):
    data = get_weather_data(city, country)
    
    # 데이터가 없으면 400 Bad request 반환 
    if not data: 
        raise HTTPException(status_code=400, 
                            detail="Data not found")
    # DB 삽입하고 새로 생성된 id를 받음 
    new_id = WeatherObservation.insert(data)
    # 응답 데이터에 id 추가 
    data["id"] = new_id
    return data

# 전체 데이터 조회 
@app.get("/observations")
def get_all():
    return WeatherObservation.select_all()

# 특정id 데이터 조회 
@app.get("/observations/{id}")
def get_one(id: int):
    result = WeatherObservation.select_by_id(id)
    
    # error handling: 없으면 404 not found 
    if not result: 
        raise HTTPException(status_code=404, detail="Not found")
    return result

# id의 notes 수정 
@app.put("/observations/{id}")
def update_note(id: int, notes: str):
    success = WeatherObservation.update_notes(id, notes)
    
    if not success: 
        raise HTTPException(status_code=404, detail="Not found")
    return {"id": id, "notes": notes}

# id 데이터 삭제 
@app.delete("/observations/{id}")
def delete_obs(id: int):
    success = WeatherObservation.delete(id)
    if not success: 
        raise HTTPException(status_code=404, detail="Not found")
    return {"deleted": id}

# 서버 실행 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)