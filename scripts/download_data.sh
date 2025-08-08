#!/bin/sh
# Эта версия скрипта совместима с POSIX sh (используется в Alpine)

URLS="\
https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet \
https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-02.parquet \
"
# Дополнительные файлы для скачивания. Добавлять на свой страх и риск - каждый новый значительно увеличивает время загрузки
# https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-03.parquet \
# https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-04.parquet \
# https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-05.parquet \
# https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-06.parquet \


for URL in $URLS; do
  FILENAME=$(basename "$URL")
  echo "Downloading $FILENAME..."
  curl -L -o "$FILENAME" "$URL"
done

echo "All data files downloaded successfully!"