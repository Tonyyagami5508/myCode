FROM python:3.11-slim

WORKDIR /app

# System deps (ca-certificates for TLS)
RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Install project
COPY . /app
RUN pip install -U pip \
  && pip install -e '.[web]'

ENV VITADV_HOST=0.0.0.0 \
    VITADV_PORT=8899 \
    PYTHONUNBUFFERED=1

EXPOSE 8899
CMD ["vitadataview-web"]
