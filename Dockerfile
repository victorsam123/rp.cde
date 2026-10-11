FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py wsgi.py cde_deployment.py ./
COPY templates ./templates
COPY static ./static
RUN mkdir -p /app/static/uploads
ENV PYTHONUNBUFFERED=1
CMD ["sh", "-c", "gunicorn wsgi:app --bind 0.0.0.0:${PORT:-5000} --workers 1 --threads 4 --timeout 120"]
