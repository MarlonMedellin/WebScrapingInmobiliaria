from sqlalchemy import create_engine, text
import os

POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secret")
POSTGRES_DB = os.getenv("POSTGRES_DB", "realestate_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

def run_sql(sql):
    with engine.connect() as conn:
        try:
            conn.execute(text(sql))
            conn.commit()
            print(f"Executed: {sql}")
        except Exception as e:
            print(f"Failed: {sql} | Error: {e}")

if __name__ == "__main__":
    run_sql("ALTER TABLE properties ADD COLUMN IF NOT EXISTS area FLOAT;")
    run_sql("ALTER TABLE properties ADD COLUMN IF NOT EXISTS bedrooms INTEGER;")
    run_sql("ALTER TABLE properties ADD COLUMN IF NOT EXISTS bathrooms INTEGER;")
    # Try to clean and convert price
    run_sql("UPDATE properties SET price = '0' WHERE price IS NULL OR price = '';")
    # For now, let's keep price as String in DB if conversion is tricky, or just add a new column
    run_sql("ALTER TABLE properties ADD COLUMN IF NOT EXISTS price_numeric FLOAT;")
    run_sql("UPDATE properties SET price_numeric = CAST(regexp_replace(price, '[^0-9.]', '', 'g') AS DOUBLE PRECISION) WHERE price ~ '[0-9]';")
