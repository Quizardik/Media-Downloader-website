FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN apt-get update && apt-get install -y \
    ffmpeg \
    nodejs \
    curl \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080
# Increase timeout to accommodate long-running downloads (age-restricted / large files)
CMD ["gunicorn", "web_app:app", "-b", "0.0.0.0:8080", "--workers", "2", "--timeout", "600"]
