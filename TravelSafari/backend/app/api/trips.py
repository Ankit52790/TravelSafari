from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.database import get_db
from app.models.models import Trip

router = APIRouter()

# -------------------------
# Schemas
# -------------------------
class Location(BaseModel):
    lat: float
    lng: float

class TripCreate(BaseModel):
    name: str
    route: List[Location]
    total_distance: float
    estimated_cost: float = 0.0

# -------------------------
# APIs
# -------------------------
@router.post("/")
def create_trip(trip: TripCreate, db: Session = Depends(get_db)):
    db_trip = Trip(
        user_id=None,  # later we will attach auth
        name=trip.name,
        route=[loc.dict() for loc in trip.route],
        total_distance=trip.total_distance,
        estimated_cost=trip.estimated_cost
    )

    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)

    return db_trip


@router.get("/")
def get_all_trips(db: Session = Depends(get_db)):
    return db.query(Trip).all()
