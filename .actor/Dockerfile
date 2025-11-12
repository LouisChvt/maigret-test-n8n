FROM python:3.12-slim
WORKDIR /app

# Installer dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf-2.0-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    git \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Copier le script principal depuis le dossier actor
COPY main.py .

# Installer Python dependencies
RUN YARL_NO_EXTENSIONS=1 python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel
RUN YARL_NO_EXTENSIONS=1 python3 -m pip install --no-cache-dir maigret apify

# Lancer le script
CMD ["python3", "main.py"]
