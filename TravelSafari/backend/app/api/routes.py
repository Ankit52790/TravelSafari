# backend\app\api\routes.py
from fastapi import APIRouter,Query ,HTTPException
from typing import List

from app.schemas.route import (
    Location,
    OptimizeRequest,
    OptimizeResponse,
    GeocodeRequest,
    GeocodeResponse
)
from app.utils.optimizer import optimize_route
from app.utils.geolocation import get_coordinates

router = APIRouter()

# -------------------
# Health Check
# -------------------
@router.get("/")
def health():
    return {"status": "Backend running 🚀"}

# -------------------
# Optimize Route
# -------------------
@router.post("/optimize", response_model=OptimizeResponse)
def optimize(req: OptimizeRequest):
    if len(req.locations) < 2:
        raise HTTPException(status_code=400, detail="At least two locations required")

    try:
        points = [loc.dict() for loc in req.locations]
        result = optimize_route(points)

        # Ensure result has both keys
        route = result.get("route", [])
        total_distance = result.get("total_distance", 0.0)

        return {
            "route": route,
            "total_distance": total_distance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------
# Geocode Place
# -------------------
@router.post("/geocode", response_model=GeocodeResponse)
def geocode(req: GeocodeRequest):
    try:
        lat, lng = get_coordinates(req.place)
        return GeocodeResponse(lat=lat, lng=lng)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
