FROM python:3.11-slim

WORKDIR /app

# Copy requirements first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Copy the rest of the application code
# Make /app visible as a package root
COPY . .
ENV PYTHONPATH=/app



EXPOSE 8000
CMD ["uvicorn", "services.api-gateway.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
