FROM python:3.11

# Install necessary dependencies and geckodriver
RUN apt-get update && apt-get install -y wget curl

# Install Poetry and configure it
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Set the working directory
WORKDIR /app

COPY app /app/app
COPY pyproject.toml poetry.lock /app/

# Install dependencies without dev packages
RUN poetry install --no-root --only main

COPY app/ ./app

# Expose the necessary ports
EXPOSE 8000

CMD ["uvicorn", "app.main:app"]