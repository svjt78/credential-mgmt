# Builder stage: compile wheels
FROM python:3.10-slim AS builder
WORKDIR /app

# install build deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt

# Final stage: lean runtime image
FROM python:3.10-slim
WORKDIR /app

# runtime libs
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# install Python deps from wheels
COPY --from=builder /app/wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links /wheels -r requirements.txt

# copy entrypoint for one-time table creation
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# copy app source
COPY . .

# serve on port 8001
EXPOSE 8001
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8001", "--workers", "4"]
