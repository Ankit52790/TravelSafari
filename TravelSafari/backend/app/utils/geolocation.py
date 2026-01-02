# backend/app/utils/geolocation.py

from opencage.geocoder import OpenCageGeocode
from app.core.config import settings

# Initialize ONCE
if not settings.OPENCAGE_API_KEY:
    raise RuntimeError("OPENCAGE_API_KEY is missing in environment")

geocoder = OpenCageGeocode(settings.OPENCAGE_API_KEY)

def get_coordinates(place_name: str):
    """
    Convert place name to (lat, lng)
    """
    try:
        results = geocoder.geocode(place_name)
    except Exception:
        raise ValueError("Geocoding service unavailable")

    if not results:
        raise ValueError(f"Could not find coordinates for '{place_name}'")

    geometry = results[0]["geometry"]
    return geometry["lat"], geometry["lng"]
