# python

import inspect
import logging
import os
import random
import time
from optparse import OptionParser

import gevent; from gevent import monkey; monkey.patch_all()
import requests
from locust import HttpLocust

from httpsession import HttpSession
from stats import Stats, StackDriverStats

import grpc.experimental.gevent as grpc_gevent; grpc_gevent.init_gevent()

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger(__name__)

TARGET_HOST = os.getenv('TARGET_HOST', 'http://localhost:5000')

NUM_USERS = int(os.getenv('NUM_USERS', '1'))

MODE_CONTINUOUS = 'continuous'
MODE_AFTER_DEPLOY = 'after_deploy'
MODE_ONE_OFF = 'one_off'
MODE = os.getenv('MODE', MODE_CONTINUOUS)
USER_WAIT_TIME_SECONDS = int(os.getenv('USER_WAIT_TIME_SECONDS', 15))
SUBMISSIONS = int(os.getenv('SUBMISSIONS', '1'))
STACKDRIVER_ENABLED = os.getenv('STACKDRIVER_ENABLED', 'false').lower() == 'true'

TEST_TYPE = os.getenv('TEST_TYPE')

# A rough value indicating the number of pages in the survey. This is used to stagger the worker start up times
SURVEY_PAGE_COUNT = 77


class ScenarioPicker:
    def __init__(self):
        assert TEST_TYPE in ('full_test', 'simple_test',)
        scenario_module = __import__(TEST_TYPE)
        self.scenarios = [v for k, v in vars(scenario_module).items() if self._is_scenario(k, v)]
        self.weights = [scenario.weight for scenario in self.scenarios]
        
    def pick(self):
        return random.choices(self.scenarios, self.weights)[0]
    
    @staticmethod
    def _is_scenario(name, item):
        return bool(
            inspect.isclass(item) and
            issubclass(item, HttpLocust) and
            hasattr(item, "task_set") and
            getattr(item, "task_set") and
            not name.startswith('_')
        )

scenario_picker = ScenarioPicker()


def worker(worker_id, stats):
    num_submissions = SUBMISSIONS if MODE != MODE_CONTINUOUS else 1

    while num_submissions > 0:
        try:
            start_time = time.time()
            client = HttpSession(base_url=TARGET_HOST, stats=stats)

            scenario = scenario_picker.pick()
            log.info('[%d] Starting %s', worker_id, scenario.__name__)

            scenario(client).run()

            log.info('[%d] Survey completed in %f seconds', worker_id, time.time() - start_time)

            if MODE != MODE_CONTINUOUS:
                num_submissions -= 1
        except Exception:
            log.exception('Error running session, will retry in 30 seconds')
            time.sleep(30)


def run_workers():
    workers = []

    if STACKDRIVER_ENABLED:
        stats = StackDriverStats()
        workers.append(gevent.spawn(stats.start_worker))
    else:
        stats = Stats()

    for i in range(NUM_USERS):
        workers.append(gevent.spawn(worker, i, stats))
        time.sleep(SURVEY_PAGE_COUNT * USER_WAIT_TIME_SECONDS / NUM_USERS)

    gevent.joinall(workers)


def get_version():
    try:
        return requests.get(TARGET_HOST + '/status').json()['version']
    except Exception:
        log.exception('Error getting version')
        return None


if __name__ == "__main__":
    if MODE == MODE_AFTER_DEPLOY:
        tested_version = current_version = get_version()

        while True:
            while current_version is None or current_version == tested_version:
                log.info('Version has not changed from %s, waiting', tested_version)
                time.sleep(30)
                current_version = get_version()

            log.info('Version has changed from %s to %s, repeating tests', tested_version, current_version)

            run_workers()

            tested_version = current_version

    run_workers()
