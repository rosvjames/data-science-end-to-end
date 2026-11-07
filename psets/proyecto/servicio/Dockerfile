# La imagen del servicio de prediccion. Se construye desde psets/proyecto/,
# porque necesita modelado/ ademas de servicio/:
#
#     python servicio/exportar_modelo.py      # genera servicio/modelo.joblib
#     docker build -f servicio/Dockerfile -t servicio-demanda .
#     docker run -p 8000:8000 servicio-demanda
FROM python:3.11-slim
WORKDIR /app
COPY servicio/requirements.txt servicio/requirements.txt
RUN pip install --no-cache-dir -r servicio/requirements.txt
COPY modelado/pipeline_proyecto.py modelado/pipeline_proyecto.py
COPY servicio/api.py servicio/modelo.joblib servicio/
EXPOSE 8000
CMD ["uvicorn", "servicio.api:app", "--host", "0.0.0.0", "--port", "8000"]
