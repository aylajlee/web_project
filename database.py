import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

# 비밀번호 확인 
print("DEBUG: DB_PASSWORD:", os.getenv("DB_PASSWORD"))

class DataManager:
    @staticmethod
    def get_connection():
        return psycopg.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )

class BaseModel:
    def __init__(self, id=None):
        self.id = id

class WeatherObservation(BaseModel):
    TABLE = "weather_observation"

    def __init__(self, city, country, latitude, longitude, 
                 temperature, elevation, windspeed, observation_time, 
                 notes=None, id=None):
        
        super().__init__(id)
        self.city = city
        self.country = country
        self.latitude = latitude
        self.longitude = longitude
        self.temperature = temperature
        self.elevation = elevation
        self.windspeed = windspeed
        self.observation_time = observation_time
        self.notes = notes

    @classmethod
    def insert(cls, data):
        with DataManager.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    INSERT INTO {cls.TABLE} (city, country, latitude, longitude, 
                    temperature, elevation, windspeed, observation_time, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
                """, (data['city'], data['country'], data['latitude'], data['longitude'], 
                      data['temperature'], data['elevation'], data['windspeed'], data['observation_time'], None))
                new_id = cur.fetchone()[0]
                conn.commit()
                return new_id

    @classmethod
    def select_all(cls):
        with DataManager.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM {cls.TABLE}")
                return cur.fetchall()

    @classmethod
    def select_by_id(cls, obs_id):
        with DataManager.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM {cls.TABLE} WHERE id = %s", (obs_id,))
                return cur.fetchone()

    @classmethod
    def update_notes(cls, obs_id, notes):
        with DataManager.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"UPDATE {cls.TABLE} SET notes = %s WHERE id = %s", (notes, obs_id))
                conn.commit()
                return cur.rowcount > 0

    @classmethod
    def delete(cls, obs_id):
        with DataManager.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"DELETE FROM {cls.TABLE} WHERE id = %s", (obs_id,))
                conn.commit()
                return cur.rowcount > 0