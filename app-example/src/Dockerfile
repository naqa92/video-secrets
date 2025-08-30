FROM python:3.13-slim

WORKDIR /app

# Copier les fichiers de l'application
COPY requirements.txt .
COPY app.py .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
