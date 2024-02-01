import logging
import os
import warnings

from locust import HttpUser, between, task

logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore")


username = os.environ.get("SERVE_USERNAME")
password = os.environ.get("SERVE_PASS")
page_rel_url = os.environ.get("PROTECTED_PAGE_RELATIVE_URL")


class AuthenticatedUser(HttpUser):
    """Simulates an authenticated user with a user account in Serve."""

    # For now only supports one fixed user
    fixed_count = 1

    wait_time = between(2, 3)

    is_authenticated = False

    def on_start(self):
        logger.debug("on start")
        self.client.verify = False  # Don't check if certificate is valid
        self.get_token()
        self.login()

    def get_token(self):
        self.client.get("/accounts/login/")
        self.csrftoken = self.client.cookies["csrftoken"]
        logger.debug("self.csrftoken = %s", self.csrftoken)

    def login(self):
        logger.info("Login as user %s", username)

        login_data = dict(username=username, password=password, csrfmiddlewaretoken=self.csrftoken)

        with self.client.post(
            url="/accounts/login/",
            data=login_data,
            headers={"Referer": "foo"},
            name="---ON START---LOGIN",
            catch_response=True,
        ) as response:
            logger.debug("login response.status_code = %s, %s", response.status_code, response.reason)
            # If login succeeds then url = /accounts/login/, else /projects/
            logger.debug("login response.url = %s", response.url)
            if "/projects" in response.url:
                self.is_authenticated = True
            else:
                response.failure(f"Login as user {username} failed. Response URL does not contain /projects")

    def logout(self):
        logger.debug("Log out user %s", username)
        # logout_data = dict(username=username, csrfmiddlewaretoken=self.csrftoken)
        self.client.get("/accounts/logout/", name="---ON STOP---LOGOUT")

    @task
    def browse_homepage(self):
        self.client.get("/home/")

    @task(2)
    def browse_protected_page(self):
        if self.is_authenticated is False:
            logger.debug("Skipping test browse_protected_page. User is not authenticated.")
            return

        request_data = dict(username=username, csrfmiddlewaretoken=self.csrftoken)

        response = self.client.get(page_rel_url, data=request_data, headers={"Referer": "foo"}, verify=False)

        with self.client.get(
            page_rel_url,
            data=request_data,
            headers={"Referer": "foo"},
            verify=False,
            catch_response=True,
        ) as response:
            logger.debug("protected page response.status_code = %s, %s", response.status_code, response.reason)
            # If login succeeds then url = ?, else ?
            logger.debug("protected page %s", response.url)
            if page_rel_url not in response.url:
                response.failure("User failed to access protected page.")

    def on_stop(self):
        logger.debug("on stop. exec logout.")
        self.logout()
