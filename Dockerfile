FROM python:3.7

RUN pip install pipenv

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

ADD docker-run.sh /docker-run.sh
ADD app /app
ADD jwt-test-keys /jwt-test-keys

RUN pipenv install --deploy --system

EXPOSE 5557 5558 8089

ENTRYPOINT ["/bin/bash", "docker-run.sh"]
