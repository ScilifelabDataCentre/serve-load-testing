"""A Locust test file."""

from locust import HttpUser, task, between
import warnings
warnings.filterwarnings("ignore")


APP_SHINYPROXY = "https://loadtest-shinyproxy2.staging.serve-dev.scilifelab.se/app/loadtest-shinyproxy2"


class AppViewerUser(HttpUser):
    """ Simulates a non-authenticated user that uses apps in Serve.
        Note: This test is not completed. The response time statistics
        do not currently reflect the true time taken to start the user app.
    """
    weight = 1
    wait_time = between(4, 8)

    def on_start(self):
        self.client.verify = False  # Don't to check if certificate is valid

    @task
    def browse_homepage(self):
        self.client.get("/home/")

    @task(2)
    def browse_apps(self):
        self.client.get("/apps/")

    @task
    def open_user_app(self):
        self.client.get(APP_SHINYPROXY, name="user-app-shiny-proxy")

    @task
    def browse_models(self):
        self.client.get("/models/")
