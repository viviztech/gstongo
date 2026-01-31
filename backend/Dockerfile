FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN python manage.py collectstatic --noinput

RUN mkdir -p logs

CMD ["gunicorn", "gstongo.wsgi:application", "--bind", "0.0.0.0:8000"]
