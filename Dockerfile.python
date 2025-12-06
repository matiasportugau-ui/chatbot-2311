# Dockerfile para el sistema Python de BMC
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear usuario no-root
RUN useradd -m -u 1000 bmc && chown -R bmc:bmc /app
USER bmc

# Exponer puerto para API (si es necesario)
EXPOSE 8000

# Variables para saltar la verificación de .venv dentro del contenedor
ENV SKIP_VENV_CHECK=true

# Comando por defecto - refrescar conocimiento y luego iniciar FastAPI
CMD ["bash", "-c", "bash scripts/refresh_knowledge.sh && python api_server.py"]
