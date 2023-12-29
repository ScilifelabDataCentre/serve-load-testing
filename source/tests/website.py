"""A Locust test file."""

from locust import HttpUser, task, between
import warnings
warnings.filterwarnings("ignore")


# Define user/scenario types

class VisitingUser(HttpUser):
    """ Simulates a casual, visiting, non-authenticated user
        that browses the public pages.
    """
    weight = 2
    wait_time = between(1, 3)

    def on_start(self):
        self.client.verify = False  # Don't to check if certificate is valid

    @task(3)
    def browse_homepage(self):
        self.client.get("/home/")

    @task
    def browse_about(self):
        self.client.get("/about/")

    @task
    def browse_apps(self):
        self.client.get("/apps/")

    @task
    def browse_models(self):
        self.client.get("/models/")
