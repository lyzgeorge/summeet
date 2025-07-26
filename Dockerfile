# Multi-stage build for single container deployment
FROM node:18-alpine as frontend-build

# Build frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Production stage - Python with built frontend
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy and install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY backend/ ./

# Copy built frontend from build stage
COPY --from=frontend-build /app/frontend/dist /usr/share/nginx/html

# Create nginx configuration for single container
RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    # Handle Vue.js SPA routing \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    \
    # Proxy API requests to backend \
    location /api/ { \
        proxy_pass http://localhost:8000/; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
    } \
    \
    # Static files caching \
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ { \
        expires 1y; \
        add_header Cache-Control "public, immutable"; \
    } \
}' > /etc/nginx/sites-available/default

# Create startup script
RUN echo '#!/bin/bash\n\
# Start nginx in background\n\
nginx -g "daemon off;" &\n\
\n\
# Start FastAPI backend\n\
cd /app\n\
uvicorn main:app --host 0.0.0.0 --port 8000\n\
' > /start.sh && chmod +x /start.sh

# Expose port 80 for the web interface
EXPOSE 80

# Start both services
CMD ["/start.sh"]