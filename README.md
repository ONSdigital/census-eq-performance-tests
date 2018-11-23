# Census EQ Performance Tests

Locust tests for load testing the census eQ survey runner user flow.

## Setup

```
brew install pyenv
pyenv install
pip install --upgrade pip setuptools pipenv
pipenv install
```

## Scenarios

Simple scenario has 2 household members and 1 visitor:

To run locally:
```
locust -f app/simple_test.py --host=http://localhost:5000 -c 100 -r 100 --noweb
```

Full test contains 11 scenarios with between 0 and 10 household members. These are weighted based on proportions derived from 2011 census results.

Three common scenarios also have a small number of visitors.

To run locally:
```
locust -f app/simple_test.py --host=http://localhost:5000 -c 100 -r 100 --noweb

```

See [locust documentation](https://docs.locust.io/en/latest/index.html) for more information on running locust tests.
