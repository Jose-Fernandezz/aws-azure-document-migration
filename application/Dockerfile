FROM python:3.14-slim

WORKDIR /app

COPY application/requirements.txt /app/application/requirements.txt

RUN pip install --no-cache-dir -r /app/application/requirements.txt

COPY application /app/application

EXPOSE 5001

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "application.app:app"]