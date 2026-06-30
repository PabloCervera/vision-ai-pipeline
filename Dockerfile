# Imagen base ligera con Python 3.11 (compatible con torch/ultralytics y las deps fijadas).
FROM python:3.11-slim

# Dependencias de sistema que OpenCV necesita para importarse en modo headless
# (sin entorno gráfico). El pipeline corre con show_window=False, así que no abre ventanas.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias primero para aprovechar la caché de capas de Docker.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto.
COPY . .

# API (FastAPI/uvicorn) y dashboard (Streamlit).
EXPOSE 8000 8501

# Comando por defecto: la API. El dashboard usa su propio comando en docker-compose.
WORKDIR /app/src
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
