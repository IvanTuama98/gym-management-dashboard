# Usa una imagen oficial de Python ligera
FROM python:3.10-slim

# Crea y define el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia primero el archivo de requerimientos para aprovechar el caché de Docker
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el resto del código del proyecto
COPY . .

# Expone el puerto donde corre tu app Flask (usualmente 5000)
EXPOSE 5000

# Comando para iniciar la aplicación
CMD ["python", "app.py"]