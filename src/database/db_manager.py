import psycopg2
from psycopg2 import OperationalError
from typing import List, Dict, Optional, Any

class DBManager:
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config

    def _get_connection(self):
        try:
            conn = psycopg2.connect(
                host=self.db_config['host'],
                port=int(self.db_config['port']),
                dbname=self.db_config['dbname'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            return conn
        except OperationalError as e:
            print(f"Ошибка подключения к БД: {e}")
            raise

    def get_countries_and_aeroplanes_count(self) -> List[Dict[str, Any]]:
        query = """
            SELECT c.name AS country_name, COUNT(a.id) AS aircraft_count
            FROM countries c
            LEFT JOIN aircrafts a ON c.name = a.origin_country
            GROUP BY c.id, c.name
            ORDER BY aircraft_count DESC;
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    columns = [desc[0] for desc in cur.description]
                    return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            print(f"Ошибка при получении статистики: {e}")
            return []

    def get_avg_speed(self) -> Optional[float]:
        query = "SELECT AVG(velocity) FROM aircrafts;"
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    result = cur.fetchone()
                    return result[0] if result and result[0] is not None else None
        except Exception as e:
            print(f"Ошибка при расчете средней скорости: {e}")
            return None

    def get_aeroplanes_with_higher_speed(self, threshold: float) -> List[Dict[str, Any]]:
        query = """
            SELECT id, icao24, callsign, velocity, latitude, longitude
            FROM aircrafts
            WHERE velocity > %s
            ORDER BY velocity DESC;
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (threshold,))
                    columns = [desc[0] for desc in cur.description]
                    return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            print(f"Ошибка поиска быстрых самолётов: {e}")
            return []

    def get_aeroplanes_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        search_pattern = f"%{keyword}%"
        query = """
            SELECT id, icao24, callsign, velocity
            FROM aircrafts
            WHERE callsign ILIKE %s
            LIMIT 20;
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (search_pattern,))
                    columns = [desc[0] for desc in cur.description]
                    return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            print(f"Ошибка поиска по ключевому слову: {e}")
            return []
