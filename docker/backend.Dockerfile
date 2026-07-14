# Build context is the repo root (see docker-compose.yml), so paths below are
# relative to ct-watch-console/, not this Dockerfile's own directory.
FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

ENV API_HOST=0.0.0.0 \
    API_PORT=5000 \
    FIXTURE_DIR=/app/fixtures

EXPOSE 5000

CMD ["python", "app.py"]
