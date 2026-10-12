FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System libs needed by opencv, librosa/soundfile and mediapipe
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 libglib2.0-0 libsndfile1 ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# fer needs TensorFlow; the CPU build is enough inside a container
RUN pip install --no-cache-dir "tensorflow-cpu>=2.20,<2.21"

COPY . .

EXPOSE 1600

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "1600"]
