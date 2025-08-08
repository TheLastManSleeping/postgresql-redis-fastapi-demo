from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TaxiTripBase(BaseModel):
    vendor_id: int
    pickup_datetime: datetime
    passenger_count: Optional[int] = None
    trip_distance: Optional[float] = None

class TaxiTripCreate(TaxiTripBase):
    pass

class TaxiTrip(TaxiTripBase):
    id: int
    class Config:
        from_attributes = True

class PassengerStats(BaseModel):
    passenger_count: int
    average_distance: float

# ... в конце файла schemas.py

class TaxiTripUpdate(BaseModel):
    vendor_id: Optional[int] = None
    pickup_datetime: Optional[datetime] = None
    passenger_count: Optional[int] = None
    trip_distance: Optional[float] = None