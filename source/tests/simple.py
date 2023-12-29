"""A Locust test file."""

from locust import HttpUser, task, between
import warnings
warnings.filterwarnings("ignore")


class SimpleUser(HttpUser):
    """ The main purpose of this test user is to verify the setup of the test framework.
    """
    wait_time = between(1, 2)

    def on_start(self):
        self.client.verify = False  # Don't to check if certificate is valid

    @task(3)
    def browse_homepage(self):
        self.client.get("/home/")
