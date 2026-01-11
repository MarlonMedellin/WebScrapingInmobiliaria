import os
from sqlalchemy import create_engine, text

# Use the Docker internal URL or localhost depending on where this runs
# We will run this from OUTSIDE via a simple direct connection if possible or inside container
# Assuming running inside Docker or having access to port 5432
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:secret@localhost:5432/realestate_db")

def migrate():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        print("Starting Migration V3...")

        # 1. Add status column to properties if not exists
        try:
            conn.execute(text("ALTER TABLE properties ADD COLUMN status VARCHAR DEFAULT 'NEW';"))
            print("✅ Added 'status' column to properties.")
        except Exception as e:
            print(f"ℹ️ Status column might already exist: {e}")

        # 2. Create saved_searches table
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS saved_searches (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR NOT NULL,
                    criteria TEXT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """))
            print("✅ Created 'saved_searches' table.")
        except Exception as e:
            print(f"❌ Error creating saved_searches table: {e}")

    print("Migration V3 Completed.")

if __name__ == "__main__":
    migrate()
