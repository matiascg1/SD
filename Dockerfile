FROM python:3.9-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Crear directorio para datos
RUN mkdir -p /app/data

# Comando por defecto
CMD ["python", "-m", "src.main"]
