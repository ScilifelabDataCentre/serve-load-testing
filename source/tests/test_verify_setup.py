"""Locust test file to verify the Locust test framework setup."""

import logging
import warnings

from locust import HttpUser, between, task

logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore")


class VerifyLocustUser(HttpUser):
    """The main purpose of this test user is to verify the setup of the Locust test framework."""

    wait_time = between(1, 2)

    def on_start(self):
        self.client.verify = False  # Don't to check if certificate is valid

    @task
    def verify_task(self):
        logger.info("executing simple task verify_task")
