# backend/Dockerfile.migration
FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies (adjust path if needed)
COPY services/api-gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- CRITICAL: Copy Alembic files ---
COPY alembic/ ./alembic/   
COPY alembic.ini .        
# --- End of critical copy ---

# Copy other necessary application code (adjust paths)
COPY common/ ./common/

CMD ["alembic", "upgrade", "head"]