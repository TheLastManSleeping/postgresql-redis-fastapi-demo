# fastapi_app/Dockerfile

FROM python:3.9-slim

WORKDIR /code

# Указываем полный путь от корня контекста сборки
COPY ./fastapi_app/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Указываем полные пути для остальных файлов
COPY ./fastapi_app/app /code/app
COPY ./scripts/init_db.py /code/init_db.py
COPY ./fastapi_app/app/sample_data.csv /code/app/sample_data.csv

# Даем права на исполнение
RUN chmod +x /code/init_db.py

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--timeout-keep-alive", "300"]