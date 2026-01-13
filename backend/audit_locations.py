import os
import sys
import json
from sqlalchemy.orm import Session

# Ensure imports work in Docker environment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from database import SessionLocal
    from models import Property
    from neighborhood_utils import auto_resolve_neighborhood
except ImportError:
    # Fallback for different execution contexts
    from backend.database import SessionLocal
    from backend.models import Property
    from backend.neighborhood_utils import auto_resolve_neighborhood

def run_audit(apply_fixes=False):
    db: Session = SessionLocal()
    try:
        # Load neighborhood map
        map_path = "neighborhood_map.json"
        if not os.path.exists(map_path):
            map_path = "backend/neighborhood_map.json"
            
        with open(map_path, "r", encoding="utf-8") as f:
            nb_map = json.load(f)

        properties = db.query(Property).all()
        
        stats = {
            "total": len(properties),
            "matched": 0,
            "enrichable": 0,
            "unknown": 0,
            "portals": {}
        }

        print(f"--- DATABASE LOCATION AUDIT ({'FIX MODE' if apply_fixes else 'REPORT MODE'}) ---")
        print(f"Total properties to analyze: {len(properties)}\n")

        updates = []

        for p in properties:
            if p.source not in stats["portals"]:
                stats["portals"][p.source] = {"total": 0, "matched": 0, "enrichable": 0, "unknown": 0}
            
            stats["portals"][p.source]["total"] += 1

            # Check if location already contains a known neighborhood/comuna
            # We use auto_resolve_neighborhood on the location first
            current_match = auto_resolve_neighborhood(p.location, nb_map)
            
            # If not matched in location, try to find it in title
            title_match = auto_resolve_neighborhood(p.title, nb_map)

            if current_match:
                stats["matched"] += 1
                stats["portals"][p.source]["matched"] += 1
            elif title_match:
                stats["enrichable"] += 1
                stats["portals"][p.source]["enrichable"] += 1
                
                # Inferred name for enrichment
                clean_name = title_match.split(" - ")[-1] if " - " in title_match else title_match
                new_location = f"{clean_name}, {p.location}"
                updates.append((p.id, p.title, p.location, new_location))
                
                if apply_fixes:
                    p.location = new_location
            else:
                stats["unknown"] += 1
                stats["portals"][p.source]["unknown"] += 1
                updates.append((p.id, p.title, p.location, "UNKNOWN"))

        # Summary Report
        print(f"Summary:")
        print(f"  - Matched (Already has neighborhood): {stats['matched']} ({stats['matched']/stats['total']*100:.1f}%)")
        print(f"  - Enrichable (Can be fixed via Title): {stats['enrichable']} ({stats['enrichable']/stats['total']*100:.1f}%)")
        print(f"  - Unknown (No neighborhood found): {stats['unknown']} ({stats['unknown']/stats['total']*100:.1f}%)")
        
        print("\nBreakdown by Portal:")
        for portal, p_stats in stats["portals"].items():
            print(f"  {portal:15}: {p_stats['matched']} matched, {p_stats['enrichable']} enrichable, {p_stats['unknown']} unknown (Total: {p_stats['total']})")

        if not apply_fixes and updates:
            print(f"\nUnknown / Suggestion Analysis:")
            for id, title, old, target in updates:
                if target == "UNKNOWN":
                    print(f"  - [ID {id}] [{title}] -> Location: {old}")
                else:
                    # Enrichable (if any were found in a future run)
                    print(f"  - [ID {id}] [ENRICH] '{title}' -> New Location: {target}")

    except Exception as e:
        print(f"Error during audit: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    mode = "--fix" in sys.argv
    run_audit(apply_fixes=mode)
