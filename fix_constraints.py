"""Добавляет уникальные ограничения, если их нет."""

from src.utils.config import load_config
import psycopg2

def main():
    cfg = load_config("config.ini")
    conn = psycopg2.connect(
        host=cfg["host"],
        port=int(cfg["port"]),
        dbname=cfg["dbname"],
        user=cfg["user"],
        password=cfg["password"]
    )

    with conn.cursor() as cur:
        # Уникальное ограничение для countries.name
        cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'countries_name_key'
                ) THEN
                    ALTER TABLE countries ADD CONSTRAINT countries_name_key UNIQUE (name);
                END IF;
            END$$;
        """)

        # Уникальное ограничение для aircrafts.icao24
        cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'aircrafts_icao24_key'
                ) THEN
                    ALTER TABLE aircrafts ADD CONSTRAINT aircrafts_icao24_key UNIQUE (icao24);
                END IF;
            END$$;
        """)

    conn.commit()
    conn.close()
    print("✅ Ограничения добавлены (или уже существовали).")

if __name__ == "__main__":
    main()
