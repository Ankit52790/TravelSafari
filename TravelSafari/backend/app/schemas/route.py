from pydantic import BaseModel
from typing import List

# -------------------
# Location Schema
# -------------------
class Location(BaseModel):
    lat: float
    lng: float

# -------------------
# Optimize Route Request & Response
# -------------------
class OptimizeRequest(BaseModel):
    locations: List[Location]

class OptimizeResponse(BaseModel):
    route: List[Location]
    total_distance: float

# -------------------
# Save Route Request & Response
# -------------------
class SaveRouteRequest(BaseModel):
    route_name: str
    route: List[Location]
    total_distance: float
    estimated_cost: float

class SavedRoute(BaseModel):
    name: str
    route: List[Location]
    total_distance: float
    estimated_cost: float

class SavedRoutesResponse(BaseModel):
    routes: List[SavedRoute]

# -------------------
# Geocode Request & Response
# -------------------
class GeocodeRequest(BaseModel):
    place: str

class GeocodeResponse(BaseModel):
    lat: float
    lng: float
