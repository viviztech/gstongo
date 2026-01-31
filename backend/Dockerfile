FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files (for Unfold + Admin)
RUN python manage.py collectstatic --noinput

RUN mkdir -p logs

CMD ["gunicorn", "gstongo.wsgi:application", "--bind", "0.0.0.0:8000"]
