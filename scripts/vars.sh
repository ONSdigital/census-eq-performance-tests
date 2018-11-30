# Your GCP project ID
PROJECT_ID=my-gcp-project-id

CLUSTER_NAME=perftest
ZONE=europe-west1-b

DOCKER_REPO=eu.gcr.io/census-ci/census-eq-performance-tests

# How many users each Locust worker should handle
USERS_PER_WORKER=800

# Time in seconds that Locust should take to get to the full user load
RAMP_UP_TIME=300

# Amount of time to run each step of the spike test for
SPIKE_STEP_RUN_TIME=900

# How many times more than the user count should the maximum spike be
# I.e. if the user count is 1,000 and this setting is 16 then the largest spike will run 16,000 users
SPIKE_MAX_USER_MULTIPLIER=16