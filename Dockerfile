FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

RUN pip install pipenv

WORKDIR /app

COPY Pipfile* ./
RUN pipenv sync

COPY . .
