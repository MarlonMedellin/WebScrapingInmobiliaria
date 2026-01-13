import os
import sys
import json
from sqlalchemy.orm import Session

# Asegurar que podemos importar desde el backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import SessionLocal
from models import Property
from neighborhood_utils import auto_resolve_neighborhood

def fix_locations():
    db: Session = SessionLocal()
    try:
        # Cargar mapa de barrios para la resolución
        map_path = "backend/neighborhood_map.json"
        with open(map_path, "r", encoding="utf-8") as f:
            nb_map = json.load(f)

        # Solo procesar propiedades de conquistadores que no tengan un barrio claro en 'location'
        properties = db.query(Property).filter(Property.source == "conquistadores").all()
        
        updated_count = 0
        print(f"Revisando {len(properties)} propiedades de conquistadores...")

        for p in properties:
            # Si el título tiene el barrio pero la localización es genérica (ej. "Medellín, Antioquia")
            # Intentamos extraer el barrio del título
            inferred_category = auto_resolve_neighborhood(p.title, nb_map)
            
            if inferred_category:
                # Si el barrio inferido del título NO está ya en la localización
                if inferred_category.lower() not in p.location.lower():
                    # Extraemos el nombre limpio (ej: "Belén" de "C16 - Belén")
                    clean_name = inferred_category.split(" - ")[-1] if " - " in inferred_category else inferred_category
                    
                    old_location = p.location
                    p.location = f"{clean_name}, {p.location}"
                    updated_count += 1
                    print(f"✅ Mejorado: '{p.title}' -> {p.location}")

        if updated_count > 0:
            db.commit()
            print(f"\n✨ Se han mejorado {updated_count} registros de ubicación.")
        else:
            print("\nNo se encontraron registros para mejorar.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_locations()
