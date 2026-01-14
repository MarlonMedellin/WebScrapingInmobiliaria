import unicodedata
import re
from typing import Optional

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
    
    # 3. Eliminar ruidos comunes
    ruidos = [
        r'\bbarrio\b', r'\bsector\b', r'\bubicacion\b', r'\bmedellin\b', 
        r'\bmunicipio\b', r'\bciudad\b', r'\bcomuna\b', r'\bantioquia\b'
    ]
    for ruido in ruidos:
        name = re.sub(ruido, '', name)
    
    # 4. Limpiar caracteres especiales y espacios múltiples
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
        for v in variants:
            if clean_name == clean_neighborhood_name(v):
                return True
    return False

def auto_resolve_neighborhood(neighborhood: str, nb_map: dict) -> Optional[str]:
    """
    Fase 2: Intenta resolver un barrio por contención de palabras clave.
    Si encuentra una coincidencia fuerte, devuelve la categoría (Ej: 'C16 - Belén').
    """
    clean_input = clean_neighborhood_name(neighborhood)
    if not clean_input or len(clean_input) < 3:
        return None

    # Lista de palabras a ignorar por ser demasiado genéricas para autocompletar
    ignore_keywords = {"la", "el", "los", "las", "del", "sur", "norte", "oriente", "occidente"}

    # Intentar coincidencia por 'contención'
    for category, variants in nb_map.items():
        for variant in variants:
            clean_variant = clean_neighborhood_name(variant)
            
            # Solo considerar variantes con palabras significativas (>3 letras)
            if len(clean_variant) < 4 or clean_variant in ignore_keywords:
                continue
            
            # Caso 1: La variante está contenida en el input (Ej: 'belen' está en 'belen de los alpes')
            # Usamos regex para asegurar que sea una palabra completa
            if re.search(rf'\b{re.escape(clean_variant)}\b', clean_input):
                return category
                
            # Caso 2: El input está contenido en la variante (Ej: 'poblado' está en 'el poblado')
            if re.search(rf'\b{re.escape(clean_input)}\b', clean_variant):
                return category

    return None

def resolve_specific_variant(neighborhood: str, nb_map: dict) -> Optional[str]:
    """
    Busca el nombre específico del barrio (la variante bonita del mapa)
    que coincida con el input sucio.
    Ej: "Calasanz, Medellín" -> "Calasanz"
    """
    clean_input = clean_neighborhood_name(neighborhood)
    if not clean_input or len(clean_input) < 3:
        return None
        
    ignore_keywords = {"la", "el", "los", "las", "del", "sur", "norte", "oriente", "occidente"}

    # Recolectar todas las variantes posibles en una lista
    all_variants = []
    for category, variants in nb_map.items():
        if isinstance(variants, list):
            all_variants.extend(variants)
            
    # CRITICO: Ordenar por longitud descendente para evitar que 
    # "Prado" haga match con "Prado Verde" antes de tiempo.
    all_variants.sort(key=lambda v: len(clean_neighborhood_name(v)), reverse=True)

    # 1. Búsqueda
    for v in all_variants:
        clean_v = clean_neighborhood_name(v)
        if len(clean_v) < 3 or clean_v in ignore_keywords:
            continue
            
        # Match Exacto
        if clean_v == clean_input:
            return v
            
        # Match Contención (Input tien variante)
        # Ej: "Casa en Prado Verde" tiene "Prado Verde" -> Match
        if re.search(rf'\b{re.escape(clean_v)}\b', clean_input):
            return v
                
    return None
