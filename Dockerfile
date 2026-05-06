# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Nginx
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies directly to avoid setuptools discovery errors
RUN pip install --no-cache-dir \
    fastapi==0.115.8 \
    pandas==2.2.3 \
    requests==2.32.3 \
    sqlalchemy==2.0.38 \
    streamlit==1.42.0 \
    uvicorn==0.40.0

# Copy Nginx config
COPY nginx.conf /etc/nginx/sites-available/default

# Create a startup script cleanly
RUN printf "#!/bin/bash\n\
python3 -m uvicorn backend:app --host 127.0.0.1 --port 4444 &\n\
streamlit run dummy_frontend.py --server.port 8501 --server.address 127.0.0.1 --server.headless true --server.enableCORS false --server.enableXsrfProtection false &\n\
nginx -g \"daemon off;\"\n" > start.sh && chmod +x start.sh

# Expose the Nginx port (Hugging Face default)
EXPOSE 7860

# Start services
CMD ["./start.sh"]
