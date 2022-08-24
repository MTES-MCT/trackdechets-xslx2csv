FROM python:3.9-bullseye

ENV PYTHONDONTWRITEBYTECODE=1

COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --dev --system --deploy

WORKDIR /app
COPY . /app