from locust import HttpLocust

from household_taskset import HouseholdTaskSet


class SurveyRunnerSimpleScenario(HttpLocust):
    task_set = HouseholdTaskSet
    household_individual_count = 2
    visitor_count = 1
