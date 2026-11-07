# Imagen del proyecto M5: corre el pipeline de preparacion de modelado/.
# Se construye desde psets/proyecto/. Los datos no van en la imagen: se montan.
#
#     docker build -t proyecto-m5 .
#     docker run --rm -v "$(pwd)/data:/app/data" proyecto-m5
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY modelado/pipeline_proyecto.py modelado/
WORKDIR /app/modelado
CMD ["python", "pipeline_proyecto.py"]
