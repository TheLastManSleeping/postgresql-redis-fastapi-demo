from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas

# --- Статистика (тяжелый запрос) ---
def get_passenger_stats(db: Session):
    return db.query(
        models.TaxiTrip.passenger_count,
        func.avg(models.TaxiTrip.trip_distance).label("average_distance")
    ).group_by(models.TaxiTrip.passenger_count).order_by(models.TaxiTrip.passenger_count).all()


# --- CRUD-операции для поездок ---

# READ (одна запись)
def get_trip(db: Session, trip_id: int):
    return db.query(models.TaxiTrip).filter(models.TaxiTrip.id == trip_id).first()

# READ (список записей с пагинацией)
def get_trips(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TaxiTrip).offset(skip).limit(limit).all()

# CREATE
def create_trip(db: Session, trip: schemas.TaxiTripCreate):
    db_trip = models.TaxiTrip(**trip.dict())
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip

# UPDATE
def update_trip(db: Session, trip_id: int, trip_update: schemas.TaxiTripUpdate):
    db_trip = get_trip(db, trip_id)
    if not db_trip:
        return None
    
    update_data = trip_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_trip, key, value)
    
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip

# DELETE
def delete_trip(db: Session, trip_id: int):
    db_trip = get_trip(db, trip_id)
    if not db_trip:
        return None
    db.delete(db_trip)
    db.commit()
    return db_trip