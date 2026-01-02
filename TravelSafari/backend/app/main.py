#📍 backend/app/main.py

from fastapi import FastAPI
from dotenv import load_dotenv

from app.api.auth import router as auth_router
from app.api.routes import router as routes_router
from app.api.trips import router as trips_router

load_dotenv()

app = FastAPI(
    title="Travel Route Optimizer API",
    version="1.0.0"
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(routes_router, tags=["Routes"])
app.include_router(trips_router, prefix="/trips", tags=["Trips"])
