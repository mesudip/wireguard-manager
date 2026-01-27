# Stage 1: Build Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app

# Accept build argument for API URL
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

COPY frontend/package.json frontend/yarn.lock* ./
RUN yarn install --frozen-lockfile
COPY frontend/ .
RUN yarn build

# Stage 2: Final Backend Image
FROM python:3.11-slim
WORKDIR /app

# Install WireGuard tools and dependencies for wg-quick
RUN apt-get update && \
    apt-get install -y wireguard-tools iproute2 iptables procps curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy backend source
COPY backend/ .
RUN pip install --no-cache-dir -r requirements.txt

# Copy built frontend from Stage 1
# The backend serves static files from /lib/wireguard/backend
RUN mkdir -p /lib/wireguard/backend
COPY --from=frontend-builder /app/dist /lib/wireguard/backend

EXPOSE 5000

# Default environment for container (can be overridden)
ENV WG_WIREGUARD_USE_SUDO=false \
    WG_WIREGUARD_USE_SYSTEMD=false \
    WG_WIREGUARD_BASE_DIR=/etc/wireguard \
    WG_SERVER_PORT=5000

# Start the application using Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--preload", "app:app"]
