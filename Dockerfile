FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="./.venv"

# Prepend poetry and venv to PATH
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    build-essential

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python -

# Set the working directory
WORKDIR /app

# Copy dependency files and install dependencies
COPY pyproject.toml poetry.lock /app/
COPY . /app
RUN poetry install --no-dev

# Set the entrypoint to your application
ENTRYPOINT ["poetry", "run", "python", "-m", "s3_synchroniser.main"]
