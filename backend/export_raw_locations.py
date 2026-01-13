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

        output_file = "raw_locations_for_curation.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# Reporte de Ubicaciones para Curación Manual\n\n")
            f.write(f"- **Total de registros:** {len(properties)}\n")
            f.write(f"- **Ubicaciones únicas:** {len(unique_locations)}\n\n")
            
            f.write("## Instrucciones\n")
            f.write("1. Revisa la tabla de ubicaciones abajo.\n")
            f.write("2. Identifica la Comuna o Municipio correcto.\n")
            f.write("3. Actualiza el archivo `neighborhood_map.json` con los nuevos hallazgos.\n\n")
            
            f.write("| Ubicación | Frecuencia | Ejemplos de Títulos |\n")
            f.write("| :--- | :--- | :--- |\n")

            # Sort by count descending to prioritize most common ones
            sorted_locs = sorted(unique_locations.items(), key=lambda x: x[1]["count"], reverse=True)

            for loc, data in sorted_locs:
                # Clean location and titles for markdown table compatibility
                clean_loc = loc.replace("|", "\\|").replace("\n", " ")
                examples = ", ".join(data['examples']).replace("|", "\\|").replace("\n", " ")
                f.write(f"| {clean_loc} | {data['count']} | {examples} |\n")

        print(f"✅ Data exported successfully to {output_file}")

    except Exception as e:
        print(f"Error during export: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    export_raw_data()
