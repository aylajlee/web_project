import psycopg
import os
from dotenv import load_dotenv

# .env(파일)에서 환경변수(DB 접속 정보)를 로드 
load_dotenv()

class DatabaseManager:
    """
    PostgreSQL 데이터베이스 연결을 관리하는 클래스
    설정 정보를 유지하고, 필요할 때마다 새로운 연결(Connection) 제공
    """
    def __init__(self):
        # 환경변수 기반 DB 연결문자열 생성 
        self.connection_string = (
            f"dbname={os.getenv('DB_NAME')} "
            f"user={os.getenv('DB_USER')} "
            f"password={os.getenv('DB_PASSWORD')} "
            f"host={os.getenv('DB_HOST', 'localhost')} "
            f"port={os.getenv('DB_PORT', '5432')}"
        )

    def get_connection(self):
        """DB에 접속하여 연결 객체를 반환"""
        return psycopg.connect(self.connection_string)

def initialize_database(db_manager, get_weather_func):
    """
    서버 시작 시 테이블을 생성하고, 기본 데이터(Chicago, Seoul, Swiss)를 자동으로 추가 
    """
    # 테이블 생성
    with db_manager.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS weather_observation (
                    id SERIAL PRIMARY KEY,
                    city VARCHAR(100) NOT NULL,
                    country VARCHAR(50) NOT NULL,
                    latitude DECIMAL(10, 8),
                    longitude DECIMAL(11, 8),
                    temperature_c DECIMAL(5, 2),
                    windspeed_kmh DECIMAL(5, 2),
                    observation_time VARCHAR(100),
                    notes TEXT
                );
            """)
            conn.commit()

    # 데이터가 비어있을 때(시작)만 예시데이터 3개 추가
    if len(WeatherObservation.all(db_manager)) == 0:
        default_cities = [("Chicago", "US"), ("Seoul", "KR"), ("Bern", "CH")]
        print("Initializing default weather data!")
        
        for city, country in default_cities:
            data = get_weather_func(city, country)
            if data:
                obs = WeatherObservation(db_manager, **data)
                obs.save()

class WeatherObservation:
    """
    날씨 관측 데이터를 나타내는 ORM(Oriented-Relational Mapping) 패턴 클래스
    각 인스턴스 - DB 테이블의 레코드(행) 하나에 대응됨
    """
    TABLE_NAME = "weather_observation"

    def __init__(self, db_manager, city, country, latitude, longitude, 
                 temperature_c, windspeed_kmh, observation_time, notes=None, id=None):
        self.db = db_manager
        self.id = id
        self.city = city
        self.country = country
        self.latitude = latitude
        self.longitude = longitude
        self.temperature_c = temperature_c
        self.windspeed_kmh = windspeed_kmh
        self.observation_time = observation_time
        self.notes = notes

    def save(self):
        """ 
        현재 객체의 상태를 DB에 저장
        ID가 없으면 -> 새로운 레코드를 생성(INSERT)하고
        ID가 있으면 -> 기존 레코드를 수정(UPDATE)
        """
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                if self.id is None:
                    # 새로운 데이터 저장: RETURNING id를 사용하여 DB가 생성한 ID를 즉시 받아옴
                    query = f"""
                        INSERT INTO {self.TABLE_NAME} 
                        (city, country, latitude, longitude, temperature_c, windspeed_kmh, observation_time, notes) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                        RETURNING id
                    """
                    
                    cur.execute(query, (
                        self.city, 
                        self.country, 
                        self.latitude, 
                        self.longitude, 
                        self.temperature_c, 
                        self.windspeed_kmh, 
                        self.observation_time, 
                        self.notes
                    ))
                    
                    result = cur.fetchone()
                    if result:
                        self.id = result[0]
                else:
                    # 기존 데이터 수정: Notes(메모) 필드만 업데이트 
                    query = f"UPDATE {self.TABLE_NAME} SET notes = %s WHERE id = %s"
                    cur.execute(query, (self.notes, self.id))
                
                # 변경사항 실제 업데이트 
                conn.commit()
                
        return self

    @classmethod
    def all(cls, db_manager):
        """DB의 모든 날씨 기록을 조회하여 객체리스트로 반환"""
        with db_manager.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT id, city, country, latitude, longitude, temperature_c, windspeed_kmh, observation_time, notes FROM {cls.TABLE_NAME}")
                rows = cur.fetchall()
                # 조회된 각 행(row)를 클래스 인스턴스로 변환 
                # e.g. r[0]은 id로, r[1:]은 나머지로 전달
                return [cls(db_manager, *r[1:], id=r[0]) for r in rows]

    @classmethod
    def get_by_id(cls, db_manager, id):
        """고유한 ID를 사용하여 특정 날씨 기록을 조회"""
        with db_manager.get_connection() as conn:
            with conn.cursor() as cur:
                query = f"SELECT id, city, country, latitude, longitude, temperature_c, windspeed_kmh, observation_time, notes FROM {cls.TABLE_NAME} WHERE id = %s"
                cur.execute(query, (id,))
                row = cur.fetchone()
                if row:
                    return cls(db_manager, *row[1:], id=row[0])
                return None

    def update_notes(self, notes):
        """Notes(메모) 내용을 변경하고, DB에 반영"""
        self.notes = notes
        self.save()

    def delete(self):
        """현재 객체에 해당하는 레코드를 DB에서 삭제"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                query = f"DELETE FROM {self.TABLE_NAME} WHERE id = %s"
                cur.execute(query, (self.id,))
                conn.commit()
