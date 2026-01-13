import os
import sys
import json
from sqlalchemy.orm import Session

# Ensure imports work in Docker environment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from database import SessionLocal
    from models import Property
except ImportError:
    from backend.database import SessionLocal
    from backend.models import Property

def export_raw_data():
    db: Session = SessionLocal()
    try:
        properties = db.query(Property).all()
        
        # We want to identify unique location strings to make it easier for the user
        unique_locations = {}
        
        for p in properties:
            loc = p.location.strip()
            if loc not in unique_locations:
                unique_locations[loc] = {
                    "examples": [],
                    "count": 0
                }
            
            unique_locations[loc]["count"] += 1
            if len(unique_locations[loc]["examples"]) < 3:
                unique_locations[loc]["examples"].append(p.title)

        output_file = "raw_locations_for_curation.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("=== REPORTE DE UBICACIONES PARA CURACIÓN MANUAL ===\n")
            f.write(f"Total de registros: {len(properties)}\n")
            f.write(f"Ubicaciones únicas: {len(unique_locations)}\n\n")
            f.write("Instrucciones:\n")
            f.write("1. Revisa las ubicaciones abajo.\n")
            f.write("2. Identifica a qué comuna o municipio pertenecen.\n")
            f.write("3. Si ves un patrón (ej: 'Centro, ENVIGADO'), agrégalo al JSON en la categoría 'Envigado'.\n\n")
            f.write("-" * 50 + "\n\n")

            # Sort by count descending to prioritize most common ones
            sorted_locs = sorted(unique_locations.items(), key=lambda x: x[1]["count"], reverse=True)

            for loc, data in sorted_locs:
                f.write(f"UBICACIÓN: {loc}\n")
                f.write(f"FRECUENCIA: {data['count']}\n")
                f.write(f"EJEMPLOS DE TÍTULOS:\n")
                for ex in data['examples']:
                    f.write(f"  - {ex}\n")
                f.write("\n")

        print(f"✅ Data exported successfully to {output_file}")

    except Exception as e:
        print(f"Error during export: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    export_raw_data()
