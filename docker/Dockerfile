FROM python:3.7

RUN pip install pipenv

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

ADD app /app
ADD jwt-test-keys /jwt-test-keys

RUN pipenv install --deploy --system

ENTRYPOINT ["python", "app/runner.py"]
