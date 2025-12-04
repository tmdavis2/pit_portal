FROM python:3.11-slim

WORKDIR /app

# Install system deps if needed
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Run migrations and collect static
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE $PORT

# Start with Gunicorn
CMD daphne pit_portal.wsgi:application --bind 0.0.0.0:$PORT
