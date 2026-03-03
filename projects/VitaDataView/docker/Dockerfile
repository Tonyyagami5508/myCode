FROM python:3.11-slim-bookworm

WORKDIR /app

# ODBC Driver 18 for SQL Server (Debian)
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
      ca-certificates curl gnupg apt-transport-https \
      unixodbc unixodbc-dev \
  && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft.gpg \
  && echo "deb [arch=arm64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
  && apt-get update \
  && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
  && rm -rf /var/lib/apt/lists/*

# Install project
COPY . /app
RUN pip install -U pip \
  && pip install -e '.[web]'

ENV VITADV_HOST=0.0.0.0 \
    VITADV_PORT=8899 \
    VITA_DB_BACKEND=odbc \
    VITA_DB_ENCRYPT=no \
    VITA_DB_TRUST_CERT=yes \
    PYTHONUNBUFFERED=1

EXPOSE 8899
CMD ["vitadataview-web"]
