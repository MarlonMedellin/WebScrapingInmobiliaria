from database import engine, Base
from models import Property, SavedSearch

def init():
    print("Iniciando creación de tablas...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas exitosamente.")

if __name__ == "__main__":
    init()
