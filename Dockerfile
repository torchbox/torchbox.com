ARG UV_VERSION=0.13.7

FROM node:26-slim AS frontend-deps

# Make build & post-install scripts behave as if we were in a CI environment (e.g. for logging verbosity purposes).
ARG CI=true

WORKDIR /app

# Install front-end dependencies.
COPY package.json package-lock.json tsconfig.json webpack.config.js ./
RUN npm ci --no-audit --progress=false

FROM frontend-deps AS frontend

# Compile static files
COPY ./tbx/ ./tbx/
RUN npm run build:prod


FROM ghcr.io/astral-sh/uv:${UV_VERSION}@sha256:96f40d3904aad8d0bd010539001d36c8e2188b981e1334471a90c4a1d93bb490 AS uv-binary

# We use Debian images because they are considered more stable than the alpine
# ones becase they use a different C compiler. Debian images also come with
# all useful packages required for image manipulation out of the box. They
# however weight a lot, approx. up to 1.5GiB per built image.
# Pinned to a particlar version as requested by support team 6/10/25
FROM python:3.15-trixie AS python-base

ARG UV_SYNC_ARGS="--no-dev"

# Install dependencies in a virtualenv
ENV VIRTUAL_ENV=/venv

RUN useradd tbx --create-home && mkdir /app $VIRTUAL_ENV && chown -R tbx /app $VIRTUAL_ENV

WORKDIR /app

RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    jpegoptim pngquant gifsicle libjpeg-progs webp \
    && apt-get autoremove && rm -rf /var/lib/apt/lists/*

# Set default environment variables. They are used at build time and runtime.
# If you specify your own environment variables on Heroku or Dokku, they will
# override the ones set here. The ones below serve as sane defaults only.
#  * PATH - Make sure that uv is on the PATH, along with our venv
#  * PYTHONUNBUFFERED - This is useful so Python does not hold any messages
#    from being output.
#    https://docs.python.org/3.9/using/cmdline.html#envvar-PYTHONUNBUFFERED
#    https://docs.python.org/3.9/using/cmdline.html#cmdoption-u
#  * DJANGO_SETTINGS_MODULE - default settings used in the container.
#  * PORT - default port used. Please match with EXPOSE so it works on Dokku.
#    Heroku will ignore EXPOSE and only set PORT variable. PORT variable is
#    read/used by Gunicorn.
#  * WEB_CONCURRENCY - number of workers used by Gunicorn. The variable is
#    read by Gunicorn.
#  * GUNICORN_CMD_ARGS - additional arguments to be passed to Gunicorn. This
#    variable is read by Gunicorn
ENV PATH=$VIRTUAL_ENV/bin:$PATH \
    UV_SYNC_ARGS=${UV_SYNC_ARGS} \
    UV_PROJECT_ENVIRONMENT=$VIRTUAL_ENV \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=tbx.settings.production \
    PORT=8000 \
    WEB_CONCURRENCY=3 \
    GUNICORN_CMD_ARGS="-c gunicorn-conf.py --max-requests 1200 --max-requests-jitter 50 --access-logfile - --timeout 25"

# Make $BUILD_ENV available at runtime
ARG BUILD_ENV
ENV BUILD_ENV=${BUILD_ENV}


# Port exposed by this container. Should default to the port used by your WSGI
# server (Gunicorn). This is read by Dokku only. Heroku will ignore this.
EXPOSE 8000

# Install uv
COPY --from=uv-binary /uv /usr/local/bin/uv

USER tbx

# Install your app's Python requirements.
RUN python -m venv $VIRTUAL_ENV
COPY --chown=tbx pyproject.toml uv.lock ./
RUN uv sync ${UV_SYNC_ARGS} --no-install-project && rm -rf $HOME/.cache


FROM python-base AS production

COPY --chown=tbx --from=frontend /app/tbx/static_compiled ./tbx/static_compiled

# Copy application code.
COPY --chown=tbx . .

# Run uv sync again to install our project (so the the tbx package is always importable)
RUN uv sync ${UV_SYNC_ARGS}

# Collect static. This command will move static files from application
# directories and "static_compiled" folder to the main static directory that
# will be served by the WSGI server.
RUN SECRET_KEY=none python manage.py collectstatic --noinput --clear

# Load shortcuts
COPY ./docker/bashrc.sh /home/tbx/.bashrc

# Run the WSGI server. It reads GUNICORN_CMD_ARGS, PORT and WEB_CONCURRENCY
# environment variable hence we don't specify a lot options below.
CMD ["gunicorn", "tbx.wsgi:application"]

# These steps won't be run on production.
# This stage branches from python-base (not production) so that local dev builds
# do not require the memory-intensive frontend webpack build — static files are
# served from the volume-mounted ./tbx directory at runtime anyway.
FROM python-base AS dev

# Swap user, so the following tasks can be run as root
USER root

# Install `psql`, useful for `manage.py dbshell`
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends postgresql-client \
    && apt-get autoremove && rm -rf /var/lib/apt/lists/*

# Restore user
USER tbx

# Load shortcuts
COPY ./docker/bashrc.sh /home/tbx/.bashrc

# Install nvm and node/npm
ARG NVM_VERSION=0.40.3
COPY --chown=tbx .nvmrc ./
RUN curl https://raw.githubusercontent.com/nvm-sh/nvm/v${NVM_VERSION}/install.sh | bash \
    && bash --login -c "nvm install --no-progress && nvm alias default $(nvm run --silent --version)"

# Pull in the node modules for the frontend (from deps-only stage, no build needed)
COPY --chown=tbx --from=frontend-deps /app/node_modules ./node_modules

# do nothing forever - exec commands elsewhere
CMD ["tail", "-f", "/dev/null"]
