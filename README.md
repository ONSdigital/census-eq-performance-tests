# Census EQ Performance Tests

Script for load testing the census eQ survey runner user flow.

## Local testing

### Setup
```
brew install pyenv
pyenv install
pip install --upgrade pip setuptools pipenv
pipenv install
```

### Scenarios

Simple scenario has 2 household members and 1 visitor:

To run locally:
```
export TEST_TYPE=simple_test
pipenv run python app/runner.py
```

Full test contains 11 scenarios with between 0 and 10 household members. These are weighted based on proportions derived from 2011 census results.

Three common scenarios also have a small number of visitors.

To run locally:
```
export TEST_TYPE=full_test
pipenv run python app/runner.py
```

## GCP testing

### Setup

1. Install kubectl with `sudo apt install kubectl`

1. Install the Google Cloud CLI `apt install google-cloud-sdk` (requires the google-cloud-sdk repo in your apt config)

1. Login to the CLI with your Google account `gcloud auth login` and `gcloud auth application-default-login`

1. Create a GCP Project with an appropriate name e.g. `census-perftest`

1. Add your product name as the PROJECT_ID in `scripts/vars.sh`

1. (Optional) Alter the `TARGET_HOST` setting in the `master.yaml` and `worker.yaml` Kubernetes manifests to point to the instance of survey runner you intend to test

### Running full test

1. Run `scripts/deploy.sh {NUMBER_OF_USERS}`

1. The test will run until you stop it

1. You can scale down the test yourself by running `kubectl scale deployment worker --replicas=0`

1. Monitor your performance tester via stackdriver. The custom custom/eq_perftest/page_load_time metric will indicate the performance as reported by the performance tester.

1. Monitor the EQ application itself via stackdriver

### Running spike test

# TODO - not yet implemented

### Updating the test scripts

If you need to alter the test scripts run `scripts/push_test_image.sh` to rebuild the docker image and push to the shared container registry
