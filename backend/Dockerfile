## This dockerfile is used for testing backend only.
## Use root dockerfile for production, as it bundles both frontend and backend.
FROM python:3.11-slim

# Install WireGuard tools and dependencies for wg-quick
RUN apt-get update && \
    apt-get install -y wireguard-tools iproute2 iptables procps curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /lib/wireguard/backend

EXPOSE 5000

CMD ["python", "app.py"]
