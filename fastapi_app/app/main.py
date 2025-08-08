from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import redis
import json
from typing import List

from . import crud, models, schemas, database
from .config import settings

app = FastAPI(title="Taxi Data API with Cache")
redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, decode_responses=True)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- CRUD Эндпоинты для поездок (taxi_trips) ---

@app.post("/trips/", response_model=schemas.TaxiTrip, tags=["CRUD"])
def create_trip(trip: schemas.TaxiTripCreate, db: Session = Depends(get_db)):
    """Создать новую запись о поездке."""
    return crud.create_trip(db=db, trip=trip)

@app.get("/trips/", response_model=List[schemas.TaxiTrip], tags=["CRUD"])
def read_trips(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список поездок с пагинацией."""
    trips = crud.get_trips(db, skip=skip, limit=limit)
    return trips

@app.get("/trips/{trip_id}", response_model=schemas.TaxiTrip, tags=["CRUD"])
def read_trip(trip_id: int, db: Session = Depends(get_db)):
    """Получить одну поездку по ID (с кэшированием)."""
    cache_key = f"trip_{trip_id}"
    
    # 1. Проверяем кэш
    cached_trip = redis_client.get(cache_key)
    if cached_trip:
        print(f"✅ Cache HIT for trip_{trip_id}!")
        return json.loads(cached_trip)
    
    # 2. Если в кэше нет - идем в БД
    print(f"❌ Cache MISS for trip_{trip_id}! Querying DB...")
    db_trip = crud.get_trip(db, trip_id=trip_id)
    if db_trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    # 3. Сохраняем в кэш
    # Используем .from_orm() для корректной сериализации
    trip_data = schemas.TaxiTrip.from_orm(db_trip).json()
    redis_client.setex(cache_key, 300, trip_data) # Кэш на 5 минут
    
    return db_trip

@app.put("/trips/{trip_id}", response_model=schemas.TaxiTrip, tags=["CRUD"])
def update_trip(trip_id: int, trip: schemas.TaxiTripUpdate, db: Session = Depends(get_db)):
    """Обновить запись о поездке по ID."""
    db_trip = crud.update_trip(db=db, trip_id=trip_id, trip_update=trip)
    if db_trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    # При обновлении данных - очищаем старый кэш
    redis_client.delete(f"trip_{trip_id}")
    return db_trip

@app.delete("/trips/{trip_id}", response_model=schemas.TaxiTrip, tags=["CRUD"])
def delete_trip(trip_id: int, db: Session = Depends(get_db)):
    """Удалить запись о поездке по ID."""
    db_trip = crud.delete_trip(db, trip_id=trip_id)
    if db_trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    # При удалении данных - очищаем старый кэш
    redis_client.delete(f"trip_{trip_id}")
    return db_trip


# --- Статистика (тяжелый запрос) ---

@app.get("/trips/stats/by-passenger-count", response_model=list[schemas.PassengerStats], tags=["Stats"])
def get_trip_stats_by_passenger_count(db: Session = Depends(get_db)):
    """Тяжелый запрос для демонстрации кэширования."""
    cache_key = "stats_by_passenger_count_v2"
    cached_stats = redis_client.get(cache_key)
    if cached_stats:
        print("✅ Cache HIT for passenger stats!")
        return json.loads(cached_stats)

    print("❌ Cache MISS! Running heavy DB query for passenger stats...")
    stats = crud.get_passenger_stats(db=db)
    stats_data = [
        {"passenger_count": row.passenger_count or 0, "average_distance": row.average_distance or 0.0}
        for row in stats
    ]
    redis_client.setex(cache_key, 600, json.dumps(stats_data))
    return stats_data