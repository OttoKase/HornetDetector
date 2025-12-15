# Dockerfile for Jetson device
# NB! Choose a tag that matches your JetPack/L4T
FROM dustynv/l4t-pytorch:r36.4.0

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (Jetson-friendly)
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3-opencv \
      libglib2.0-0 \
      libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

RUN python3 -m pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY infer.py /app/infer.py
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

ENTRYPOINT ["/app/run.sh"]
