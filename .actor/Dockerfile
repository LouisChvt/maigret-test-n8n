FROM python:3.12-slim
WORKDIR /app

# Installer dépendances système + jq + jo (pour JSON)
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
    jq \
 && rm -rf /var/lib/apt/lists/*

# Installer jo (JSON output tool)
RUN curl -L https://github.com/jpmens/jo/releases/download/1.9/jo-1.9.tar.gz | tar xz \
    && cd jo-1.9 \
    && ./configure \
    && make \
    && make install \
    && cd .. \
    && rm -rf jo-1.9

# Copier tout le projet (dockerContext = ../)
COPY . .

# Installer Python dependencies
RUN YARL_NO_EXTENSIONS=1 python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel
RUN YARL_NO_EXTENSIONS=1 python3 -m pip install --no-cache-dir maigret

# Installer Apify CLI
RUN npm install -g apify-cli

# Rendre le script exécutable
RUN chmod +x actor/actor.sh

# Lancer le script
CMD ["sh", "actor/actor.sh"]
