#backend\app\models\models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# --------------------------
# User table
# --------------------------
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    trips = relationship("Trip", back_populates="user")


# --------------------------
# Trip / Route table
# --------------------------
class Trip(Base):
    __tablename__ = "trips"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    route = Column(JSON, nullable=False)  # store list of {"lat":.., "lng":..}
    total_distance = Column(Float)
    estimated_cost = Column(Float)
    
    user = relationship("User", back_populates="trips")
