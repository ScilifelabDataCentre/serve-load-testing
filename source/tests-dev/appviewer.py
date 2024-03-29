"""A Locust test file."""

import logging
import warnings

from locust import HttpUser, between, task

logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore")


class AppViewerUser(HttpUser):
    """Simulates a non-authenticated user that uses apps in Serve.
    Note: This test is not completed. The response time statistics
    do not currently reflect the true time taken to start the user app.
    """

    weight = 1
    wait_time = between(4, 8)

    def on_start(self):
        self.client.verify = False  # Don't to check if certificate is valid

    @task
    def open_user_app(self):
        """Note that this approach does not create any pods on k8s."""
        logger.info("executing task open_user_app, running on host: %s", self.host)
        # ex: https://loadtest-shinyproxy2.staging.serve-dev.scilifelab.se/app/loadtest-shinyproxy2
        # from host: https://staging.serve-dev.scilifelab.se
        APP_SHINYPROXY = self.host.replace("https://", "https://loadtest-shinyproxy2.")
        APP_SHINYPROXY += "/app/loadtest-shinyproxy2"
        logger.info("making GET request to URL: %s", APP_SHINYPROXY)
        self.client.get(APP_SHINYPROXY, name="user-app-shiny-proxy")
