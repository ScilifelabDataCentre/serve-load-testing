"""A Locust test file."""

from locust import HttpUser, task, between
import warnings
warnings.filterwarnings("ignore")


class OpenAPIClientUser(HttpUser):
    """ Simulates client systems making OpenAPI requests. """
    weight = 1
    wait_time = between(0.5, 2)

    def on_start(self):
        self.client.verify = False  # Don't to check if certificate is valid

    @task
    def call_api_info(self):
        self.client.get("/openapi/v1/api-info", verify=False)

    @task
    def call_system_version(self):
        self.client.get("/openapi/v1/system-version", verify=False)

    @task
    def get_public_apps(self):
        self.client.get("/openapi/v1/public-apps", verify=False)
