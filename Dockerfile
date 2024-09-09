# syntax=docker/dockerfile:1

FROM python:3.10 as poetry

# Poetry configuration
# See https://github.com/python-poetry/poetry/discussions/1879
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VERSION="1.8.2"

# Create virtual environment and install Poetry from PyPI
# See https://python-poetry.org/docs/#ci-recommendations
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    python3 -m venv $POETRY_HOME && \
    $POETRY_HOME/bin/pip install poetry==$POETRY_VERSION && \
    ln -s $POETRY_HOME/bin/poetry /usr/local/bin/poetry


FROM poetry as requirements-stage

# Set poetry-plugin-export version
ENV POETRY_PLUGIN_EXPORT_VERSION="1.6.0"

# Install poetry-plugin-export
RUN --mount=type=cache,target=/root/.cache/pypoetry/cache,sharing=locked \
    poetry self add poetry-plugin-export==$POETRY_PLUGIN_EXPORT_VERSION

WORKDIR /app

# Generate requirements.txt
RUN --mount=type=bind,source=poetry.lock,target=poetry.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    poetry export --only main --format requirements.txt --without-hashes --output requirements.txt


FROM poetry as build-stage

# Disable cleaning APT cache as we are using cache mounts
RUN rm -f /etc/apt/apt.conf.d/docker-clean

# Install build dependencies
# hadolint ignore=DL3008
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev

WORKDIR /app

COPY . ./

# Build project
RUN --mount=type=cache,target=/root/.cache/pypoetry/cache,sharing=locked \
    poetry build


FROM python:3.10-slim as runtime-stage

# Disable cleaning APT cache as we are using cache mounts
RUN rm -f /etc/apt/apt.conf.d/docker-clean

# Install libpq-dev required for Psycopg
# See https://www.psycopg.org/docs/install.html
# hadolint ignore=DL3008
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev

# TODO: Create user
# See https://docs.bridgecrew.io/docs/ensure-that-a-user-for-the-container-has-been-created

WORKDIR /app

ENV VIRTUAL_ENV=/app/venv

RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    --mount=type=bind,source=/app/requirements.txt,from=requirements-stage,target=requirements.txt \
    python3 -m venv $VIRTUAL_ENV && \
    $VIRTUAL_ENV/bin/pip install --upgrade -r ./requirements.txt

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    --mount=type=bind,source=/app/dist,from=build-stage,target=dist \
    $VIRTUAL_ENV/bin/pip install ./dist/*.whl

ARG DOMAIN="localhost"

ARG HOST="0.0.0.0"

ARG PORT=8765

ENV DOMAIN=$DOMAIN

ENV HOST=$HOST

ENV PORT=$PORT

EXPOSE $PORT

# TODO: Add healthcheck
# See https://docs.bridgecrew.io/docs/ensure-that-healthcheck-instructions-have-been-added-to-container-images

CMD [ "sh", "-c", "solara run --host $HOST --port $PORT --production tma.multipages" ]
