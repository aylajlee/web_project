import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

# 비밀번호 확인 
# print("DEBUG: DB_PASSWORD:", os.getenv("DB_PASSWORD"))

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

class BaseModel:
    TABLE_NAME = ""

    def __init__(self, db_manager):
        self.db = db_manager
        self.id = None

    def save(self):
        if self.id is None:
            return self._insert()
        else:
            return self._update()

    def _insert(self): raise NotImplementedError
    
    def _update(self): raise NotImplementedError
    
    def delete(self): raise NotImplementedError

class WeatherObservation(BaseModel):
    TABLE_NAME = "weather_observation"

    def __init__(self, db_manager, city, country, 
                 latitude, longitude, 
                 temperature, elevation, windspeed,
                 observation_time, 
                 notes=None, id=None):
        
        super().__init__(db_manager)
        
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

    def _insert(self):
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                query = f"""
                INSERT INTO {self.TABLE_NAME} (city, country, latitude, longitude, 
                            temperature, elevation, windspeed, observation_time, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
                """
                cur.execute(query, (self.city, self.country, self.latitude, self.longitude, 
                                    self.temperature, self.elevation, self.windspeed, self.observation_time, self.notes))
                self.id = cur.fetchone()[0]
                conn.commit()
        return self

    def _update(self):
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                query = f"UPDATE {self.TABLE_NAME} SET notes = %s WHERE id = %s"
                cur.execute(query, (self.notes, self.id))
                conn.commit()
        return self

    def delete(self):
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                query = f"DELETE FROM {self.TABLE_NAME} WHERE id = %s"
                cur.execute(query, (self.id,))
                conn.commit()
                return True

    @classmethod
    def find_by_id(cls, db_manager, obs_id):
        with db_manager.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM {cls.TABLE_NAME} WHERE id = %s", (obs_id,))
                row = cur.fetchone()
                if row:
                    return WeatherObservation(db_manager, *row[1:], id=row[0])
        return None

    @classmethod
    def all(cls, db_manager):
        with db_manager.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM {cls.TABLE_NAME}")
                rows = cur.fetchall()
                return [WeatherObservation(db_manager, *r[1:], id=r[0]) for r in rows]