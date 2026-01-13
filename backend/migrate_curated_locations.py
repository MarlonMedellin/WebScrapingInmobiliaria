import os
import sys
import json
from sqlalchemy.orm import Session
import re

# Ensure imports work in Docker environment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from database import SessionLocal
    from models import Property
    from neighborhood_utils import clean_neighborhood_name
except ImportError:
    from backend.database import SessionLocal
    from backend.models import Property
    from backend.neighborhood_utils import clean_neighborhood_name

def migrate():
    db: Session = SessionLocal()
    try:
        # Load detailed map
        map_path = "backend/detailed_curated_map.json"
        if not os.path.exists(map_path):
            map_path = "detailed_curated_map.json"
            
        with open(map_path, "r", encoding="utf-8") as f:
            detailed_map = json.load(f)

        properties = db.query(Property).all()
        
        updated_count = 0
        
        print(f"--- MIGRACIÓN DE ALTA PRECISIÓN ---")
        print(f"Propiedades a procesar: {len(properties)}\n")

        for p in properties:
            match_found = False
            best_barrio = None
            best_comuna = None
            
            # Check both location and title
            text_to_check = f"{p.location} | {p.title}"
            clean_text = clean_neighborhood_name(text_to_check)

            # We iterate over the curated list
            for comuna, barrios in detailed_map.items():
                for barrio, variants in barrios.items():
                    for v in variants:
                        clean_v = clean_neighborhood_name(v)
                        if not clean_v: continue
                        
                        # Match whole word
                        if re.search(rf'\b{re.escape(clean_v)}\b', clean_text):
                            match_found = True
                            best_barrio = barrio
                            best_comuna = comuna
                            break
                    if match_found: break
                if match_found: break

            if match_found:
                # Prepare new location
                # Avoid double prefixing
                if best_barrio.lower() in p.location.lower():
                    # Already has barrio, maybe just update format or skip
                    pass
                
                # We prefix with [Barrio] [Comuna]
                # If it's a municipality (Envigado, etc.), we don't need a comuna tag
                comuna_tag = "" if best_comuna in ["Envigado", "Sabaneta", "Itagüí", "La Estrella", "Otros Municipios"] else f"{best_comuna}, "
                prefix = f"{best_barrio}, {comuna_tag}"
                
                # Check if already prefixed
                if p.location.startswith(prefix):
                    continue

                p.location = f"{prefix}{p.location}"
                updated_count += 1
                if updated_count % 50 == 0:
                    print(f"Procesados {updated_count}...")

        db.commit()
        print(f"\n✅ MIGRACIÓN COMPLETADA. {updated_count} registros actualizados.")

    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
