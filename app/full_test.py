from locust import HttpLocust

from household_taskset import HouseholdTaskSet


class SurveyRunnerScenarioMixin:
    task_set = HouseholdTaskSet


class ScenarioA(SurveyRunnerScenarioMixin, HttpLocust):
    household_individual_count = 0
    visitor_count = 0
    weight = 2


class ScenarioB(SurveyRunnerScenarioMixin, HttpLocust):
    household_individual_count = 1
    visitor_count = 0
    weight = 11


class ScenarioC(SurveyRunnerScenarioMixin, HttpLocust):
    household_individual_count = 2
    visitor_count = 2
    weight = 13


class ScenarioD(SurveyRunnerScenarioMixin, HttpLocust):
    household_individual_count = 3
    visitor_count = 2
    weight = 6


class ScenarioE(SurveyRunnerScenarioMixin, HttpLocust):
    household_individual_count = 4
    visitor_count = 1
    weight = 5


class ScenarioF(SurveyRunnerScenarioMixin, HttpLocust):
    household_individual_count = 5
    visitor_count = 0
    weight = 2


class ScenarioG(SurveyRunnerScenarioMixin, HttpLocust):
    household_individual_count = 6
    visitor_count = 0
    weight = 1


class ScenarioH(SurveyRunnerScenarioMixin, HttpLocust):
    household_individual_count = 7
    visitor_count = 0
    weight = 1


class ScenarioI(SurveyRunnerScenarioMixin, HttpLocust):
    household_individual_count = 8
    visitor_count = 0
    weight = 1


class ScenarioJ(SurveyRunnerScenarioMixin, HttpLocust):
    household_individual_count = 9
    visitor_count = 0
    weight = 1


class ScenarioK(HttpLocust, SurveyRunnerScenarioMixin):
    household_individual_count = 10
    visitor_count = 0
    weight = 1
