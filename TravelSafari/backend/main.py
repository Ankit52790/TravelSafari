# backend/main.py
import os
from get_google_directions import get_google_directions

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

import sqlite3
import json
from typing import List

from geolocation import get_coordinates
from fastapi import HTTPException
from optimizer import optimize_route as ga_optimize_route
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

BASE_FARE = 30.0      # INR
PER_KM = 12.0         # INR per km
PER_STOP = 10.0       # INR per extra stop


def estimate_cost(total_distance_km: float, n_stops: int) -> float:
    """Simple cost model: base + per km + per intermediate stop."""
    return BASE_FARE + PER_KM * total_distance_km + PER_STOP * max(0, n_stops - 1)


# -----------------------------
# CORS setup
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# -----------------------------
# Database init
# -----------------------------
DB_PATH = "routes.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS routes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        route TEXT,
        total_distance REAL,
        estimated_cost REAL
    )
"""
)

conn.commit()

# -----------------------------
# Request Models
# -----------------------------
class Location(BaseModel):
    lat: float
    lng: float

class RouteRequest(BaseModel):
    locations: List[Location]


class OptimizedRouteResponse(BaseModel):
    route: List[Location]
    total_distance: float
    estimated_cost: float
    
class SaveRouteRequest(BaseModel):
    route: List[Location]
    route_name: str
    total_distance: float
    estimated_cost: float       # ⬅️ add this
   
class SavedRoute(BaseModel):
    name: str
    route: List[Location]
    total_distance: float
    estimated_cost: float

class SavedRoutesResponse(BaseModel):
    routes: List[SavedRoute]

class DirectionsRequest(BaseModel):
    locations: List[str]  # addresses or "lat,lng" strings

class DirectionsResponse(BaseModel):
    route: List[Location]  # reuse Location model
    
class GeocodeRequest(BaseModel):
    place_name: str

class GeocodeResponse(BaseModel):
    lat: float
    lng: float
    

# -----------------------------
# API Endpoints
# -----------------------------
@app.post("/optimize", response_model=OptimizedRouteResponse)
def optimize_route_api(req: RouteRequest):
    points = [{"lat": loc.lat, "lng": loc.lng} for loc in req.locations]
    result = ga_optimize_route(points)  # {'route': [...], 'total_distance': x}

    dist = result["total_distance"]
    optimized_points = result["route"]
    cost = estimate_cost(dist, len(optimized_points))

    # convert dicts to Location models
    optimized_locations = [Location(**p) for p in optimized_points]

    return OptimizedRouteResponse(
        route=optimized_locations,
        total_distance=dist,
        estimated_cost=cost,
    )


@app.post("/save_route")
def save_route(req: SaveRouteRequest):
    cursor.execute(
        "INSERT INTO routes (name, route, total_distance, estimated_cost) VALUES (?, ?, ?, ?)",
        (
            req.route_name,
            json.dumps([loc.dict() for loc in req.route]),
            req.total_distance,
            req.estimated_cost,
        ),
    )
    conn.commit()
    return {
        "status": "saved",
        "name": req.route_name,
        "total_distance": req.total_distance,
        "estimated_cost": req.estimated_cost,
    }


@app.get("/get_routes", response_model=SavedRoutesResponse)
def get_saved_routes():
    cursor.execute("SELECT name, route, total_distance, estimated_cost FROM routes")
    rows = cursor.fetchall()
    routes = []
    for row in rows:
        name, route_json, total_distance, estimated_cost = row
        raw_points = json.loads(route_json)
        locations = [Location(**p) for p in raw_points]
        routes.append(
            SavedRoute(
                name=name,
                route=locations,
                total_distance=total_distance,
                estimated_cost=estimated_cost,
            )
        )
    return SavedRoutesResponse(routes=routes)

@app.post("/google_directions", response_model=DirectionsResponse)
def google_directions_api(req: DirectionsRequest):
    if not GOOGLE_API_KEY:
        return {"route": []}  # or raise HTTPException(500, "API key not configured")

    result = get_google_directions(GOOGLE_API_KEY, req.locations)
    if "error" in result:
        # better: raise HTTPException(400, result["error"])
        return {"route": []}

    points = result["route"]  # list of {"lat": .., "lng": ..}
    locations = [Location(**p) for p in points]
    return DirectionsResponse(route=locations)

@app.post("/geocode", response_model=GeocodeResponse)
def geocode_api(req: GeocodeRequest):
    try:
        lat, lng = get_coordinates(req.place_name)
        return GeocodeResponse(lat=lat, lng=lng)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
