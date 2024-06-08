FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier requirements.txt et installer les dépendances
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application
COPY . .

# Exposer le port (si nécessaire, par exemple si vous avez une interface web pour le bot)
# EXPOSE 8000

# Lancer le bot
CMD ["python", "bot.py"]
