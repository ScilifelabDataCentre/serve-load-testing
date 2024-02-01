"""Locust test file to verify the Locust test framework setup and access to the SUT host."""

import warnings

from locust import HttpUser, between, task

warnings.filterwarnings("ignore")


class VerifyHostUser(HttpUser):
    """The main purpose of this test user is to verify the setup of the Locust test framework
    and access to the host.
    """

    wait_time = between(1, 2)

    def on_start(self):
        self.client.verify = False  # Don't to check if certificate is valid

    @task(3)
    def browse_homepage(self):
        self.client.get("/home/")
