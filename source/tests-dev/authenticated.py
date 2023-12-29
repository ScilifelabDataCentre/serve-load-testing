import os
from locust import HttpUser, task, between

import warnings
warnings.filterwarnings("ignore")


username = os.environ.get("SERVE_USERNAME")
password = os.environ.get("SERVE_PASS")
page_rel_url = os.environ.get("PROTECTED_PAGE_RELATIVE_URL")


class AuthenticatedUser(HttpUser):
    """ Simulates an authenticated user with a user account in Serve.
    """

    # For now only supports one fixed user
    fixed_count = 1

    wait_time = between(2, 3)

    def on_start(self):
        print("DEBUG: on start")
        self.client.verify = False  # Don't check if certificate is valid
        self.get_token()
        self.login()

    def get_token(self):
        self.client.get("/accounts/login/")
        self.csrftoken = self.client.cookies['csrftoken']
        print(f"DEBUG: self.csrftoken = {self.csrftoken}")

    def login(self):
        print(f"DEBUG: Logging in as user {username}")
        login_data = dict(username=username, password=password, csrfmiddlewaretoken=self.csrftoken)
        response = self.client.post(
            url="/accounts/login/",
            data=login_data,
            headers={"Referer": "foo"},
            name="---ON START---LOGIN")
        print(f"DEBUG: login response.status_code = {response.status_code}")

    def logout(self):
        print(f"DEBUG: Logging out user {username}")
        logout_data = dict(username=username, csrfmiddlewaretoken=self.csrftoken)
        self.client.get("/accounts/logout/", name="---ON STOP---LOGOUT")

    @task
    def browse_homepage(self):
        self.client.get("/home/")

    @task(2)
    def browse_protected_page(self):
        request_data = dict(username=username, csrfmiddlewaretoken=self.csrftoken)
        self.client.get(page_rel_url, data=request_data, headers={"Referer": "foo"}, verify=False)

    def on_stop(self):
        print("DEBUG: on stop")
        self.logout()
