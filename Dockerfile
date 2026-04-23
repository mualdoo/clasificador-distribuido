# Usa una imagen ligera de Python
FROM python:3.11-slim

# Evita que Python genere archivos .pyc y permite ver logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instalar dependencias del sistema necesarias para PyMuPDF y herramientas de red
RUN apt-get update && apt-get install -y \
    build-essential \
    libmupdf-dev \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY src/ ./src/

# Comando para arrancar el nodo
CMD ["python", "src/main.py"]