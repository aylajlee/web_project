import requests
import os
from dotenv import load_dotenv
import psycopg

# Import the Flask app
from routes import app

## Milestone 3
load_dotenv()
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
 
## Milestone 1 and 2
class Weather:
    # information: city, country, latitude, longitude, temperature, elevation, windspeed, and observation time
    def __init__(self, city, country, latitude, longitude, temperature, elevation, windspeed, observation_time):
        # 파라미터로 받은 위 데이터를
        # 객체속성(object attribute)에 할당
        self.city = city
        self.country = country
        self.latitude = latitude
        self.longitude = longitude
        self.temperature = temperature
        self.elevation = elevation
        self.windspeed = windspeed
        self.observation_time = observation_time
    
    # __str__ 함수 구현하기 
    def __str__(self):
        return (f"\nWeather Observation\n"
                f"City: {self.city}, {self.country}\n"
                f"Latitude: {self.latitude}\n"
                f"Longitude: {self.longitude}\n"
                f"Temperature: {self.temperature}\n"
                f"Elevation: {self.elevation}\n"
                f"Windspeed: {self.windspeed}\n"
                f"Observation time: {self.observation_time}\n"
                )
        
# Make safe_get using error handling like in the lecture [Week 4]
def safe_get(url, **kwargs):
    try:
        # Good habit: set a timeout so the request does not hang
        user_response = requests.get(url, timeout=10, **kwargs)
        
        # Good habit: always check ".ok"
        if user_response.ok:
            return user_response
        else:
            print("Failed:", user_response.status_code)
            return None
        
    except requests.exceptions.RequestException as e:
        print("Network error:", e)
        return None
    
def get_connection():
    # return psycopg.Connection 
    return psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )
 
def save_observation(city, country, latitude, longitude, temperature, elevation, windspeed, observation_time):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    # INSERT INTO observations (city, country, latitude, longitude, temperature, elevation, windspeed, observation_time)
                    # VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                    (city, country, latitude, longitude, temperature, elevation, windspeed, observation_time),
                )
                connection.commit()
    except Exception as e:
        print("DB insert error:", e)

def count_observations():
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM observations;")
                return cursor.fetchone()[0]
    except Exception as e:
        print("DB count error:", e)
        return 0


def average_temperature():
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT AVG(temperature) FROM observations;")
                return cursor.fetchone()[0]
    except Exception as e:
        print("DB avg error:", e)
        return None
 
def min_temperature():
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT MIN(temperature) FROM observations;")
                return cursor.fetchone()[0]
    except Exception as e:
        print("DB min error:", e)
        return None


def max_temperature():
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT MAX(temperature) FROM observations;")
                return cursor.fetchone()[0]
    except Exception as e:
        print("DB max error:", e)
        return None

def count_by_city():
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT city, COUNT(*)
                    FROM observations
                    GROUP BY city
                    ORDER BY city;
                    """
                    )
                return cursor.fetchall()
    except Exception as e:
        print("DB group by error:", e)
        return []
                    
                    
                    
                              
def main():
    # Input values for city and country  
    city = "Chicago"
    country = "US"
    
    # a
    
    # 교안에서 URL = ", params = {}, response = requests.get()
    # 2. geocoding에 맞게 URL과 params를 
    # .json으로 parsing해서 latitude와 longitude를 받아오기
    # https://geocoding-api.open-meteo.com/v1/search 
    # url = " https://geocoding-api.open-meteo.com/v1/search"
    
    # 변수명 url로 하면 안 되는 이유!!!
    # url이 2개 존재하므로 -> 반드시 어떤 url인지 구분할 수 있도록 적기 
    # 헷갈리지 않게 변수명 geocoding을 붙이기 
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {
        # Open-Meteo Geocoding API의 파라미터 그대로 name, country, count 
        "name": city, # name 그대로
        "country": country, 
        "count": 1,
    }
    
    # r = requests.get(URL, params={"userId": 2}, headers=headers, timeout=10)
    # 위 방식을 safe_get으로 해결할 수 있음    
    geo_response = safe_get(geo_url, params = geo_params)
    # 결과가 없을 경우 에러핸들링 
    if not geo_response or not geo_response.ok or "results" not in geo_response.json():
        print("City couldn't be found.")
        return 
    
    geo_data = geo_response.json()
    # 필요한 데이터 꺼내기 
    first_data = geo_data["results"][0]
    # 불러온 데이터에서 latitude, longitude 가져오기
    latitude = first_data["latitude"]
    longitude = first_data["longitude"]
    
    # b
    
    # 3. 위와 똑같은 방식으로
    # 이번에는 weather forecast API 호출하기 
    # https://api.open-meteo.com/v1/forecast?current_weather=true
    weather_url = "https://api.open-meteo.com/v1/forecast?current_weather=true"
    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True
    }
    
    
    # 응답을 먼저 받고나서 -> 에러 체크 -> json으로 변환하기
    ## initial_weather_response = requests.get(weather_url, params = weather_params, timeout=10)
    # error handling
    ## initial_weather_response.raise_for_status() 
    # 그리고나서 json 변환 
    ## json_weather_response = initial_weather_response.json()
    
    ## current_weather_response = json_weather_response['current_weather']
    
    weather_response = safe_get(weather_url, params = weather_params)
    
    if not weather_response or not weather_response.ok:
        print("It is failed to retrieve weather data.")
        return 
    
    print(f'Weather Status Code: {weather_response.status_code}')
    
    weather_data = weather_response.json()
    
    current_weather = weather_data['current_weather']
    
    # c
    
    # instance 만들고나서 출력 
    user_weather = Weather(
        # city, country, latitude, longitude, temperature, elevation, windspeed, observation_time):
        city = city,
        country = country,
        latitude = latitude,
        longitude = longitude,
        temperature = current_weather['temperature'],
        elevation = weather_data['elevation'],
        windspeed = current_weather['windspeed'],
        observation_time = current_weather['time'],
    )
    
    # print()
    
    print(user_weather)
    
    print("All object data: ", vars(user_weather))
    
    save_observation(
        user_weather.city,
        user_weather.country,
        user_weather.latitude,
        user_weather.longitude,
        user_weather.temperature,
        user_weather.elevation,
        user_weather.windspeed,
        user_weather.observation_time,
    )
    
    print("Total observations:", count_observations())
    print("Average temperature:", average_temperature())
    print("Min temperature:", min_temperature())
    print("Max temperature:", max_temperature())
    print("Count by city:", count_by_city())
    
if __name__ == "__main__":
    ## Milestone 1 테스트용 
    # main() 
    
    ## Milestone 2 
    # 여기서 서버 시작됨 
    app.run(debug=True)
 