# EOL base image, root user, secrets in layers. On purpose.
FROM python:3.6.8-stretch

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt || true

COPY . .

# secrets baked into the image
ENV SECRET_KEY=not-so-secret-fr-fr-no-cap
ENV DB_PASSWORD=hunter2
ENV PYTHONHTTPSVERIFY=0
ENV FLASK_DEBUG=1

RUN chmod -R 777 /app

EXPOSE 5000

# debug server as root on all interfaces
CMD ["python", "app.py"]
