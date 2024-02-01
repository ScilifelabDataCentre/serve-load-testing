import os
import warnings

from locust import HttpUser, between, task

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
        print("DEBUG: on start")
        self.client.verify = False  # Don't check if certificate is valid
        self.get_token()
        self.login()

    def get_token(self):
        self.client.get("/accounts/login/")
        self.csrftoken = self.client.cookies["csrftoken"]
        print(f"DEBUG: self.csrftoken = {self.csrftoken}")

    def login(self):
        print(f"DEBUG: Login as user {username}")

        login_data = dict(
            username=username, password=password, csrfmiddlewaretoken=self.csrftoken
        )

        with self.client.post(
            url="/accounts/login/",
            data=login_data,
            headers={"Referer": "foo"},
            name="---ON START---LOGIN",
            catch_response=True,
        ) as response:
            print(
                f"DEBUG: login response.status_code = {response.status_code}, {response.reason}"
            )
            # if login succeeds then url = /accounts/login/, else /projects/
            print(f"DEBUG: login response.url = {response.url}")
            if "/projects" in response.url:
                self.is_authenticated = True
            else:
                response.failure(
                    f"Login as user {username} failed. Response URL does not contain /projects"
                )

    def logout(self):
        print(f"DEBUG: Log out user {username}")
        logout_data = dict(username=username, csrfmiddlewaretoken=self.csrftoken)
        self.client.get("/accounts/logout/", name="---ON STOP---LOGOUT")

    @task
    def browse_homepage(self):
        self.client.get("/home/")

    @task(2)
    def browse_protected_page(self):
        if self.is_authenticated is False:
            print("Skipping test browse_protected_page. User is not authenticated.")
            return

        request_data = dict(username=username, csrfmiddlewaretoken=self.csrftoken)

        response = self.client.get(
            page_rel_url, data=request_data, headers={"Referer": "foo"}, verify=False
        )

        with self.client.get(
            page_rel_url,
            data=request_data,
            headers={"Referer": "foo"},
            verify=False,
            catch_response=True,
        ) as response:
            print(
                f"DEBUG: protected page response.status_code = {response.status_code}, {response.reason}"
            )
            # if login succeeds then url = ?, else ?
            print(f"DEBUG: protected page {response.url=}")
            if page_rel_url not in response.url:
                response.failure("User failed to access protected page.")

    def on_stop(self):
        print("DEBUG: on stop")
        self.logout()
