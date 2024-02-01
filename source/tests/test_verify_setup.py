"""Locust test file to verify the Locust test framework setup."""

from locust import HttpUser, task, between
import warnings

warnings.filterwarnings("ignore")


class VerifyLocustUser(HttpUser):
    """The main purpose of this test user is to verify the setup of the Locust test framework."""

    wait_time = between(1, 2)

    def on_start(self):
        self.client.verify = False  # Don't to check if certificate is valid

    @task
    def verify_task(self):
        print(f"executing simple task verify_task")
