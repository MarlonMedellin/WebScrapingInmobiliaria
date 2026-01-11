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
    # Drop and rename to ensure 'price' is a FLOAT column
    run_sql("ALTER TABLE properties RENAME COLUMN price TO price_str;")
    run_sql("ALTER TABLE properties ADD COLUMN price FLOAT;")
    run_sql("UPDATE properties SET price = CAST(regexp_replace(price_str, '[^0-9.]', '', 'g') AS DOUBLE PRECISION) WHERE price_str ~ '[0-9]';")
