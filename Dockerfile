# Imagen de Python
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# Carpeta dentro del contenedor
WORKDIR /app

# Copia la lista de librerías y las instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código de tu proyecto al contenedor
COPY . .

# Configuramos Python para que encuentre la carpeta 'src' sin problemas
ENV PYTHONPATH=/app

