# Stage 1: Build the React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
# Copy package files and install dependencies
COPY frontend/package*.json ./
RUN npm install
# Copy the rest of the frontend code and build
COPY frontend/ .
RUN npm run build

# Stage 2: Setup the FastAPI Backend
FROM python:3.11-slim
WORKDIR /app

# Copy the requirements and install them
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY backend/ /app/backend/

# Copy the built React app from Stage 1
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Hugging Face Spaces strictly requires applications to run on port 7860
EXPOSE 7860

# Change working directory so Python can resolve the 'app' module
WORKDIR /app/backend

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]