import json
import os
import sys

# Asegurar que podemos importar desde el backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.neighborhood_utils import auto_resolve_neighborhood, is_neighborhood_in_map, clean_neighborhood_name

def sync_neighborhoods():
    """
    Script de mantenimiento para procesar descubrimientos pendientes,
    auto-mapearlos si es posible y limpiar la lista.
    """
    map_path = "backend/neighborhood_map.json"
    disc_path = "backend/discovered_neighborhoods.json"
    
    if not os.path.exists(disc_path) or not os.path.exists(map_path):
        print("Archivos no encontrados.")
        return

    with open(map_path, "r", encoding="utf-8") as f:
        nb_map = json.load(f)
    
    with open(disc_path, "r", encoding="utf-8") as f:
        discovered = json.load(f)

    if not discovered:
        print("No hay barrios nuevos por procesar.")
        return

    print(f"--- Procesando {len(discovered)} barrios descubiertos ---")
    
    new_mappings = 0
    still_unknown = []
    
    for item in discovered:
        # 1. ¿Ya existe (tal vez se añadió manualmente hace poco)?
        if is_neighborhood_in_map(item, nb_map):
            continue
            
        # 2. Intentar auto-resolución
        category = auto_resolve_neighborhood(item, nb_map)
        if category:
            if item not in nb_map[category]:
                nb_map[category].append(item)
                new_mappings += 1
                print(f"✅ AUTO-MAPEADO: '{item}' -> '{category}'")
        else:
            still_unknown.append(item)

    # 3. Guardar cambios en el mapa
    if new_mappings > 0:
        with open(map_path, "w", encoding="utf-8") as f:
            json.dump(nb_map, f, indent=4, ensure_ascii=False)
        print(f"\n✨ Se han añadido {new_mappings} nuevos mapeos automáticos.")

    # 4. Actualizar lista de pendientes (solo los que no se pudieron mapear)
    with open(disc_path, "w", encoding="utf-8") as f:
        json.dump(still_unknown, f, indent=2, ensure_ascii=False)
    
    if still_unknown:
        print(f"📝 Quedan {len(still_unknown)} barrios que requieren revisión manual en {disc_path}")
    else:
        print("🎉 ¡Todos los barrios han sido procesados y mapeados!")

if __name__ == "__main__":
    sync_neighborhoods()
