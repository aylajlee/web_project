import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.connection_string = (
            f"dbname={os.getenv('DB_NAME')} "
            f"user={os.getenv('DB_USER')} "
            f"password={os.getenv('DB_PASSWORD')} "
            f"host={os.getenv('DB_HOST', 'localhost')} "
            f"port={os.getenv('DB_PORT', '5432')}"
        )

    def get_connection(self):
        return psycopg.connect(self.connection_string)

class WeatherObservation:
    TABLE_NAME = "weather_observation"

    def __init__(self, db_manager, city, country, latitude, longitude, temperature, elevation, windspeed, observation_time, notes=None, id=None):
        self.db = db_manager
        self.id = id
        self.city = city
        self.country = country
        self.latitude = latitude
        self.longitude = longitude
        self.temperature = temperature
        self.elevation = elevation
        self.windspeed = windspeed
        self.observation_time = observation_time
        self.notes = notes

    def save(self):
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                if self.id is None:
                    # 데이터 삽입 및 생성된 ID 반환
                    query = f"""
                        INSERT INTO {self.TABLE_NAME} 
                        (city, country, latitude, longitude, temperature, elevation, windspeed, observation_time, notes) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
                        RETURNING id
                    """
                    cur.execute(query, (
                        self.city, self.country, self.latitude, self.longitude, 
                        self.temperature, self.elevation, self.windspeed, 
                        self.observation_time, self.notes
                    ))
                    
                    # RETURNING id 값을 self.id에 저장
                    result = cur.fetchone()
                    if result:
                        self.id = result[0]
                else:
                    # 기존 데이터의 notes 업데이트
                    query = f"UPDATE {self.TABLE_NAME} SET notes = %s WHERE id = %s"
                    cur.execute(query, (self.notes, self.id))
                
                # 커밋을 호출하여 DB에 최종 반영
                conn.commit()
        return self


    @classmethod
    def all(cls, db_manager):
        with db_manager.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT id, city, country, latitude, longitude, temperature, elevation, windspeed, observation_time, notes FROM {cls.TABLE_NAME}")
                rows = cur.fetchall()
                # r[0]은 id로, r[1:]은 나머지 속성으로 전달
                return [cls(db_manager, *r[1:], id=r[0]) for r in rows]

    @classmethod
    def get_by_id(cls, db_manager, id):
        with db_manager.get_connection() as conn:
            with conn.cursor() as cur:
                query = f"SELECT id, city, country, latitude, longitude, temperature, elevation, windspeed, observation_time, notes FROM {cls.TABLE_NAME} WHERE id = %s"
                cur.execute(query, (id,))
                row = cur.fetchone()
                if row:
                    return cls(db_manager, *row[1:], id=row[0])
                return None

    def update_notes(self, notes):
        self.notes = notes
        self.save()

    def delete(self):
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                query = f"DELETE FROM {self.TABLE_NAME} WHERE id = %s"
                cur.execute(query, (self.id,))
                conn.commit()
