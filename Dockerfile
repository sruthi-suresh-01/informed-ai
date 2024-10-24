# Stage 1: Build Stage
FROM python:3.12-slim-bullseye AS builder
RUN pip install poetry==1.4.2

# Install necessary tools for AWS CLI installation, gnupg for apt-key, and build-essential for make
RUN apt-get update && \
    apt-get install -y curl unzip gnupg build-essential libgeos-dev && \
    # Clean up the cache and unnecessary packages to keep the image size down
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    apt-key update

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        gcc python3-dev

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root

# Stage 2: Final Image
FROM python:3.12-slim-bullseye

RUN apt-get update && \
         apt-get install -y procps

# Create a new user
RUN useradd -m agent

# Change the permissions of the /tmp directory
RUN chmod 1777 /tmp -R

# Switch to the new user
USER agent

ENV VIRTUAL_ENV=/home/agent/.venv \
    PATH="/home/agent/.venv/bin:$PATH"

RUN mkdir /home/agent/app -p

COPY --from=builder --chown=agent:agent /app/.venv ${VIRTUAL_ENV}

# Workaround to fix the shebang of the alembic script
RUN sed -i '1 s|#!/app/.venv/bin/python|#!/home/agent/.venv/bin/python|' /home/agent/.venv/bin/alembic
RUN alembic --version

WORKDIR /home/agent/app

# Copy the application source code
COPY --chown=agent:agent main.py alembic.ini ./
COPY --chown=agent:agent migrations migrations
COPY --chown=agent:agent informed informed

# We run on port 3001 (Note: this is just for documentation purposes)
EXPOSE 3001

ARG APP_VERSION
ENV APP_VERSION=${APP_VERSION}

# Run the application
ENTRYPOINT ["python", "./main.py"]
