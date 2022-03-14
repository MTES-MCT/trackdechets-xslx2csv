FROM python:3.9-bullseye

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
ENV PATH="/root/.poetry/bin/:${PATH}"
RUN mkdir -p /app/src
ADD pyproject.toml /app
ADD poetry.lock /app
RUN cd /app && poetry install
WORKDIR /app/src




