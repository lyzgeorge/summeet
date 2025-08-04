# Multi-stage build for backend-only deployment
FROM node:18-alpine AS frontend-build

# Build frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Production stage - Python backend only
FROM python:3.12-slim

# Install system dependencies (removed nginx)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy and install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY backend/ ./

# Create data directory with proper permissions
RUN mkdir -p /app/data && chmod 755 /app/data

# Copy built frontend to serve statically from FastAPI
COPY --from=frontend-build /app/frontend/dist ./static

# Expose port 8000 for the FastAPI backend
EXPOSE 8000

# Start FastAPI backend only
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]