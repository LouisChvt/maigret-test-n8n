# Garder la base du Dockerfile existant, puis ajouter :

# Installer Apify SDK
RUN pip install apify

# Copier les fichiers de l'acteur
COPY main.py /app/main.py
COPY actor.json /app/actor.json
COPY INPUT_SCHEMA.json /app/INPUT_SCHEMA.json

# Définir le point d'entrée
CMD ["python3", "/app/main.py"]
