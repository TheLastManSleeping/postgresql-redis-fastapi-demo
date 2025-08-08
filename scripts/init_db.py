import pandas as pd
from sqlalchemy import create_engine
import os
import time
import glob

print("DB Initializer started. Waiting for PostgreSQL...")
time.sleep(15)

db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)

# Проверяем, существует ли таблица, и если да, очищаем ее для полной перезагрузки
try:
    with engine.connect() as connection:
        if engine.dialect.has_table(connection, "taxi_trips"):
            print("Table 'taxi_trips' already exists. Deleting old data for a clean reload.")
            # Используем TRUNCATE для быстрой очистки таблицы
            connection.execute("TRUNCATE TABLE taxi_trips")
        else:
            print("Table 'taxi_trips' does not exist. It will be created.")
except Exception as e:
    print(f"Table check failed, proceeding. Error: {e}")

# Импортируем и создаем схему из моделей
from app.models import Base
Base.metadata.create_all(bind=engine)

# Находим все .parquet файлы в директории
data_dir = '/data/'
parquet_files = glob.glob(os.path.join(data_dir, '*.parquet'))

if not parquet_files:
    print("ERROR: No Parquet files found. Please run the download script first.")
    exit(1)

print(f"Found {len(parquet_files)} files to process: {[os.path.basename(f) for f in parquet_files]}")

start_time = time.time()
total_rows = 0

# Колонки, которые мы хотим видеть в нашей базе данных
target_columns_map = {
    'VendorID': 'vendor_id',
    'tpep_pickup_datetime': 'pickup_datetime',
    'passenger_count': 'passenger_count',
    'trip_distance': 'trip_distance'
}

# Обрабатываем каждый файл в цикле
for file_path in parquet_files:
    try:
        print(f"--- Processing file: {os.path.basename(file_path)} ---")
        df = pd.read_parquet(file_path)

        # Находим, какие из нужных нам колонок есть в этом файле
        available_original_cols = [col for col in target_columns_map.keys() if col in df.columns]

        if not available_original_cols:
            print(f"WARNING: Skipping file {os.path.basename(file_path)} as it contains none of the required columns.")
            continue

        # Выбираем только те колонки, которые существуют в файле
        df_filtered = df[available_original_cols]

        # Переименовываем их
        df_renamed = df_filtered.rename(columns=target_columns_map)

        # Если какой-то колонки не было в файле, добавляем ее с пустыми значениями
        for target_name in target_columns_map.values():
            if target_name not in df_renamed.columns:
                df_renamed[target_name] = None

        # Приводим типы и заполняем пропуски
        df_renamed['passenger_count'] = pd.to_numeric(df_renamed['passenger_count'], errors='coerce').fillna(0).astype(int)
        df_renamed['trip_distance'] = pd.to_numeric(df_renamed['trip_distance'], errors='coerce').fillna(0.0)
        df_renamed['vendor_id'] = pd.to_numeric(df_renamed['vendor_id'], errors='coerce').fillna(0).astype(int)
        df_renamed['pickup_datetime'] = pd.to_datetime(df_renamed['pickup_datetime'], errors='coerce')


        # Загружаем в БД
        df_renamed.to_sql('taxi_trips', engine, if_exists='append', index=False, chunksize=10000)
        total_rows += len(df_renamed)
        print(f"Loaded {len(df_renamed)} rows. Total rows so far: {total_rows}")

    except Exception as e:
        print(f"CRITICAL ERROR processing file {os.path.basename(file_path)}: {e}")
        print("Skipping this file and continuing with the next one.")


end_time = time.time()
print("\nFinished loading all files!")
print(f"Total records in DB: {total_rows}")
print(f"Total data loading took {end_time - start_time:.2f} seconds.")