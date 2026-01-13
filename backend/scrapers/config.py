import os
import json
import unicodedata
from ..neighborhood_utils import clean_neighborhood_name, is_neighborhood_in_map, auto_resolve_neighborhood

SEARCH_CRITERIA = {
    "operation": "arriendo",
    "property_types": ["apartamento", "casa", "apartaestudios", "loft", "estudio"],
    # Ahora el filtro base es por ciudad/municipio
    "target_cities": ["medellin", "medellín", "envigado", "itagui", "itagüí", "sabaneta", "la estrella", "estrella"],
    "max_price": 5000000,
    "initial_limit": 50,
    "scroll_depth": 10
}

def normalize_text(text: str) -> str:
    """
    Normalize text: lowercase and remove accents.
    """
    if not text:
        return ""
    text = text.lower()
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
    return text

def update_discovered_neighborhoods(neighborhood: str):
    """
    Fase 2: Automatización Progresiva.
    1. Si el barrio ya está mapeado, no hace nada.
    2. Si no está mapeado pero se puede auto-resolver (contiene palabras clave),
       se añade AUTOMÁTICAMENTE al mapa de barrios.
    3. Si no hay forma de resolverlo, se añade a la lista de descubrimientos.
    """
    if not neighborhood: return
    
    nb_map_path = os.path.join(os.path.dirname(__file__), "..", "neighborhood_map.json")
    try:
        with open(nb_map_path, "r", encoding="utf-8") as f:
            nb_map = json.load(f)
        
        # 1. Ya existe exacto o normalizado (Fase 1)
        if is_neighborhood_in_map(neighborhood, nb_map):
            return
            
        # 2. Intentar Auto-Resolución (Fase 2)
        category = auto_resolve_neighborhood(neighborhood, nb_map)
        if category:
            # ¡Auto-Mapeo! Lo añadimos al JSON oficial
            if neighborhood not in nb_map[category]:
                nb_map[category].append(neighborhood)
                with open(nb_map_path, "w", encoding="utf-8") as f:
                    json.dump(nb_map, f, indent=4, ensure_ascii=False)
                print(f"🤖 [Auto-Map] '{neighborhood}' asignado automáticamente a '{category}'")
            return

    except Exception as e:
        print(f"Error procesando auto-resolución: {e}")

    # 3. Si llegamos aquí, no hubo match. Registrar en descubrimientos para revisión manual.
    file_path = os.path.join(os.path.dirname(__file__), "..", "discovered_neighborhoods.json")
    try:
        discovered = []
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    discovered = json.loads(content)
        
        clean_new = clean_neighborhood_name(neighborhood)
        if not any(clean_neighborhood_name(d) == clean_new for d in discovered):
            discovered.append(neighborhood)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(discovered, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error actualizando descubrimientos: {e}")

def should_include_property(title: str, location: str) -> bool:
    """
    Ahora permite Inclusion General si coincide con las ciudades objetivo.
    También registra el barrio para descubrimiento.
    """
    if not title and not location:
        return False

    norm_title = normalize_text(title)
    norm_location = normalize_text(location)
    
    # 1. Registro para descubrimiento (siempre que parezca una ubicación)
    if location:
        # Intentar extraer el barrio si viene en formato "Ciudad, Barrio" o similar
        parts = [p.strip() for p in location.split(",")]
        # Asumimos que el último o penúltimo suele ser el barrio específico en muchos portales
        for part in parts:
            if part.lower() not in SEARCH_CRITERIA["target_cities"]:
                update_discovered_neighborhoods(part)

    # 2. Filtro de Inclusión (Ciudades permitidas)
    target_cities = [normalize_text(c) for c in SEARCH_CRITERIA["target_cities"]]
    
    for city in target_cities:
        if city in norm_title or city in norm_location:
            return True
            
    return False
