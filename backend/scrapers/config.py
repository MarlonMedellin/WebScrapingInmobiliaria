import unicodedata

SEARCH_CRITERIA = {
    "operation": "arriendo",
    "property_types": ["apartamento", "casa", "apartaestudios", "loft", "estudio"],
    "neighborhoods": [
        "santa fe", "santafe", "santa fé", 
        "san pablo", "sanpablo",
        "campo amor", "campoamor", "campos de amor"
    ],
    "max_price": 5000000,
    "initial_limit": 50,  # Primeros 50 inmuebles
    "scroll_depth": 10    # Scrolls para alcanzar ~50 resultados
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

def should_include_property(title: str, location: str) -> bool:
    """
    Check if property matches neighborhood criteria based on title and location.
    
    Args:
        title (str): Property title
        location (str): Property location/sector
        
    Returns:
        bool: True if property matches criteria, False otherwise.
    """
    if not title and not location:
        return False

    norm_title = normalize_text(title)
    norm_location = normalize_text(location)
    
    target_neighborhoods = [normalize_text(n) for n in SEARCH_CRITERIA["neighborhoods"]]

    for neighborhood in target_neighborhoods:
        if neighborhood in norm_title or neighborhood in norm_location:
            return True
            
    return False
