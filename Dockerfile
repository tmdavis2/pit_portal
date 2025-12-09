FROM python:3.11-slim

WORKDIR /app

# Install system deps if needed
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Collect static files (but don't run migrations here)
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Start with Daphne for ASGI (if using channels) or Gunicorn for WSGI
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "pit_portal.asgi:application"]
