FROM public.ecr.aws/docker/library/python:3.12

WORKDIR /code

COPY ./src /code/src
COPY ./env /code/env

COPY ./pyproject.toml /code/pyproject.toml
COPY ./poetry.lock /code/poetry.lock

RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-root

CMD ["poetry", "run", "uvicorn", "--app-dir", "src", "organization_management_backend_service.main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "2"]