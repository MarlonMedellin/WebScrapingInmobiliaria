from sqlalchemy import create_engine, text
import os

POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secret")
POSTGRES_DB = os.getenv("POSTGRES_DB", "realestate_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

def migrate():
    with engine.connect() as conn:
        print("Adding new columns to properties table...")
        try:
            # Change price to float
            conn.execute(text("ALTER TABLE properties ALTER COLUMN price TYPE DOUBLE PRECISION USING price::double precision;"))
        except Exception as e:
            print(f"Note on price column: {e}")
            
        try:
            conn.execute(text("ALTER TABLE properties ADD COLUMN IF NOT EXISTS area FLOAT;"))
            conn.execute(text("ALTER TABLE properties ADD COLUMN IF NOT EXISTS bedrooms INTEGER;"))
            conn.execute(text("ALTER TABLE properties ADD COLUMN IF NOT EXISTS bathrooms INTEGER;"))
            conn.commit()
            print("Successfully added columns.")
        except Exception as e:
            print(f"Error adding columns: {e}")

if __name__ == "__main__":
    migrate()
