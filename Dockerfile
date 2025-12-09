FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN apt-get update && apt-get install -y ffmpeg --no-install-recommends && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080
CMD ["gunicorn", "web_app:app", "-b", "0.0.0.0:8080", "--workers", "2"]
