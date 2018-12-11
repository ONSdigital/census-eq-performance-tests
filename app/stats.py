import logging
import os
import time

import requests

from google.cloud import monitoring_v3

log = logging.getLogger(__name__)

class Stats:
    def __init__(self):
        self.page_load_times = []

    def record(self, load_time):
        self.page_load_times.append(load_time)


class StackDriverStats(Stats):
    def __init__(self):
        super().__init__()

        self.sample_rate = os.environ.get('STACKDRIVER_SAMPLE_RATE', 60)
        self.project_id = os.environ['STACKDRIVER_PROJECT_ID']
        self.cluster_name = os.environ['STACKDRIVER_CLUSTER_NAME']
        self.container_name = os.environ['STACKDRIVER_CONTAINER_NAME']
        self.namespace_id = os.environ['STACKDRIVER_NAMESPACE_UID']
        self.pod_id = os.environ['STACKDRIVER_POD_UID']
        self.buckets = os.environ.get('STACKDRIVER_BUCKETS', 40)
        self.growth_factor = os.environ.get('STACKDRIVER_GROWTH_FACTOR', 1.4)
        self.scale = os.environ.get('STACKDRIVER_SCALE', 1)

        self.instance_id = requests.get("http://metadata.google.internal./computeMetadata/v1/instance/id", headers={'Metadata-Flavor': 'Google'}).text
        zone = requests.get("http://metadata.google.internal./computeMetadata/v1/instance/zone", headers={'Metadata-Flavor': 'Google'}).text
        self.zone = zone.split('/')[-1]

        self.client = monitoring_v3.MetricServiceClient()

    def start_worker(self):
        while True:
            time.sleep(self.sample_rate)
            self._do_push()

    def _do_push(self):
        if not self.page_load_times:
            return
        
        try:
            series = monitoring_v3.types.TimeSeries()
            series.metric.type = 'custom.googleapis.com/eq_perftest/page_load_time'
            # series.metric.labels
            series.resource.type = 'gke_container'
            series.resource.labels['project_id'] = self.project_id
            series.resource.labels['cluster_name'] = self.cluster_name
            series.resource.labels['container_name'] = self.container_name
            series.resource.labels['instance_id'] = self.instance_id
            series.resource.labels['namespace_id'] = self.namespace_id
            series.resource.labels['pod_id'] = self.pod_id
            series.resource.labels['zone'] = self.zone
            point = series.points.add()

            point.value.distribution_value.count = len(self.page_load_times)
            mean = sum(self.page_load_times) / len(self.page_load_times)
            point.value.distribution_value.mean = mean
            point.value.distribution_value.sum_of_squared_deviation = sum((t - mean) ** 2 for t in self.page_load_times)

            point.value.distribution_value.bucket_options.exponential_buckets.num_finite_buckets = self.buckets
            point.value.distribution_value.bucket_options.exponential_buckets.growth_factor = self.growth_factor
            point.value.distribution_value.bucket_options.exponential_buckets.scale = self.scale

            counts = [0] * self.buckets
            for p in self.page_load_times:
                counts[self.get_stackdriver_bucket(p)] += 1
            point.value.distribution_value.bucket_counts.extend(counts)

            now = time.time()
            point.interval.end_time.seconds = int(now)
            point.interval.end_time.nanos = int((now - point.interval.end_time.seconds) * 10 ** 9)

            self.page_load_times.clear()

            log.info('Sending metrics to stackdriver')
            self.client.create_time_series(self.client.project_path(self.project_id), [series])
        except Exception:
            log.exception('Error sending metrics to stackdriver')

    def get_stackdriver_bucket(self, page_load_time):
        for i in range(self.buckets - 1):
            if page_load_time < self.scale * self.growth_factor ** i:
                return i

        return self.buckets - 1
