import unicodedata
import re

def clean_neighborhood_name(name: str) -> str:
    """
    Normaliza el nombre de un barrio eliminando ruidos comunes, 
    acentos y caracteres especiales.
    Ej: "Barrio Belén, Medellín" -> "belen"
    """
    if not name:
        return ""
    
    # 1. Pasar a minúsculas
    name = name.lower()
    
    # 2. Eliminar acentos
    name = unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode("utf-8")
    
    # 3. Eliminar ruidos comunes (Palabras que no aportan al nombre del sector)
    # Se eliminan como palabras completas para evitar borrar "La" en "Laureles"
    ruidos = [
        r'\bbarrio\b', r'\bsector\b', r'\bubicacion\b', r'\bmedellin\b', 
        r'\benvigado\b', r'\bitagui\b', r'\bsabaneta\b', r'\bla estrella\b',
        r'\bmunicipio\b', r'\bciudad\b', r'\bcomuna\b'
    ]
    for ruido in ruidos:
        name = re.sub(ruido, '', name)
    
    # 5. Limpiar caracteres especiales y espacios múltiples
    name = re.sub(r'[^a-z0-9\s]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name

def is_neighborhood_in_map(neighborhood: str, nb_map: dict) -> bool:
    """
    Verifica si un barrio (o su forma normalizada) ya existe en el mapa.
    """
    clean_name = clean_neighborhood_name(neighborhood)
    if not clean_name:
        return False
        
    for category, variants in nb_map.items():
        # Normalizar todas las variantes del mapa para comparar
        for v in variants:
            if clean_name == clean_neighborhood_name(v):
                return True
    return False
