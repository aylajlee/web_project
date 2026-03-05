import requests
 
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
        return f"Weather in {self.city}: {self.temperature}° C"

# 4주차 교안처럼 error handling을 safe_get 방식으로 만들기
def safe_get(url, **kwargs):
    try:
        # professor said good habit (1) is setting a timeout to avoid hanging)
        user_response = requests.get(url, timeout=10, **kwargs)
        
        # professor said good habit (2) is ALWAYS checking ".ok"
        if user_response.ok:
            return user_response.json()
        else:
            print("Failed:", user_response.status_code)
            return None
        
    except requests.exceptions.RequestException as e:
        print("Network error:", e)
        return None

def main():
    # 교안에서 했던 것: URL, params, response, print("문구", response.변수)
    # 1. 입력값(도시 및 나라)  
    city = "Suwon"
    country = "KR"
    
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
    geo_data = safe_get(geo_url, params = geo_params)
    # 결과가 없을 경우 에러핸들링 
    if not geo_data or "results" not in geo_data:
        print("City couldn't be found.")
        return 
    
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
    initial_weather_response = safe_get(weather_url, params = weather_params)
    
    if not initial_weather_response:
        print("It is failed to retrieve weather data.")
        return 
    
    current_weather_response = initial_weather_response['current_weather']
    
    # c
    
    # instance 만들고나서 출력 
    user_weather = Weather(
        # city, country, latitude, longitude, temperature, elevation, windspeed, observation_time):
        city = city,
        country = country,
        latitude = latitude,
        longitude = longitude,
        temperature = current_weather_response['temperature'],
        elevation = initial_weather_response['elevation'],
        windspeed = current_weather_response['windspeed'],
        observation_time = current_weather_response['time'],
    )
    
    # print()
    
    print(user_weather)
    
    print("All object data: ", vars(user_weather))

if __name__ == "__main__":
    main()
    