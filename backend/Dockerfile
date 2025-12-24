FROM python:3.11-slim

# Install WireGuard tools
RUN apt-get update && \
    apt-get install -y wireguard-tools iproute2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create wireguard directory
RUN mkdir -p /etc/wireguard/wg-api

EXPOSE 5000

CMD ["python", "app.py"]
