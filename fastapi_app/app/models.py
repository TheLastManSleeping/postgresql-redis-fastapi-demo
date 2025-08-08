from sqlalchemy import Column, Integer, Float, DateTime
from .database import Base

class TaxiTrip(Base):
    __tablename__ = "taxi_trips"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, index=True)
    pickup_datetime = Column(DateTime, index=True)
    passenger_count = Column(Integer)
    trip_distance = Column(Float)