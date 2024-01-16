import os
from locust import HttpUser, task, between

import warnings
warnings.filterwarnings("ignore")


SERVE_LOCUST_TEST_USER_PASS = os.environ.get("SERVE_LOCUST_TEST_USER_PASS")



class VisitingBaseUser(HttpUser):
    """ Base class for a visiting website user type that may also register a new user account in Serve.
        Simulates a casual, visiting, non-authenticated user that browses the public pages.    
    """
    abstract = True

    user_type = None
    user_individual_id = 0
    local_individual_id = 0

    def get_user_id():
        """ Increments the class property user_individual_id.
            Used to assign a unique id to each individual of this user type.
        """
        VisitingBaseUser.user_individual_id += 1
        return VisitingBaseUser.user_individual_id

    def on_start(self):
        """ Called when a User starts running. """
        self.client.verify = False  # Don't check if certificate is valid
        self.local_individual_id = VisitingBaseUser.get_user_id()
        print(f"ONSTART new user type {self.user_type}, individual {self.local_individual_id}")

    # Tasks

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

    @task
    def browse_user_guide(self):
        self.client.get("/docs/")

    # TODO: register new user (max once per user instance)



class PowerBaseUser(HttpUser):
    """ Base class for the power user type that logs into Serve using an existing user account,
        then creates resources such as a project and app and finally deleted the app. 
    """
    abstract = True

    user_type = None
    user_individual_id = 0
    local_individual_id = 0

    username = "NOT_FOUND"
    password = SERVE_LOCUST_TEST_USER_PASS

    is_authenticated = False
    task_has_run = False

    def get_user_id():
        """ Increments the class property user_individual_id.
            Used to assign a unique id to each individual of this user type.
        """
        PowerBaseUser.user_individual_id += 1
        return PowerBaseUser.user_individual_id

    def on_start(self):
        """ Called when a User starts running. """
        self.client.verify = False  # Don't check if certificate is valid
        self.local_individual_id = PowerBaseUser.get_user_id()
        print(f"ONSTART new user type {self.user_type}, individual {self.local_individual_id}")
        # TODO: make user id dynamic = f"locust_test_user_{self.local_individual_id}@test.uu.net"
        self.username = "locust_test_persisted_user@test.uu.net"

    # Tasks

    @task
    def power_user_task(self):
        if self.task_has_run is True:
            print(f"Skipping power user task for user {self.local_individual_id}. It has already been run.")
            return

        self.task_has_run = True

        print(f"executing power user task")

        # Open the home page
        self.client.get("/home/")

        # Open the login page and get the csrf token
        self.get_token()

        # Login as user locust_test_user_{id}@test.uu.net
        self.login()

        if self.is_authenticated is False:
            return

        # TODO: create project: locust_test_project_new_<id>

        # TODO: create JupyterLab app

        # TODO: open the app

        # Open user docs pages
        self.client.get("/docs/")

        # TODO: delete the app

        # TODO: delete the project

        # Logout the user
        self.logout()


    def get_token(self):
        self.client.get("/accounts/login/")
        self.csrftoken = self.client.cookies['csrftoken']
        print(f"DEBUG: self.csrftoken = {self.csrftoken}")

    def login(self):
        print(f"DEBUG: Login as user {self.username}")
        
        login_data = dict(username=self.username, password=self.password, csrfmiddlewaretoken=self.csrftoken)
        
        with self.client.post(url="/accounts/login/", data=login_data, headers={"Referer": "foo"}, name="---ON START---LOGIN", catch_response=True) as response:
                print(f"DEBUG: login response.status_code = {response.status_code}, {response.reason}")
                # if login succeeds then url = /accounts/login/, else /projects/
                print(f"DEBUG: login response.url = {response.url}")
                if "/projects" in response.url:
                    self.is_authenticated = True
                else:
                    response.failure(f"Login as user {self.username} failed. Response URL does not contain /projects")

    def logout(self):
        print(f"DEBUG: Login out user {self.username}")
        logout_data = dict(username=self.username, csrfmiddlewaretoken=self.csrftoken)
        self.client.get("/accounts/logout/", name="---ON STOP---LOGOUT")



class AppViewerUser(HttpUser):
    """ Base class for app viewer user that opens up a user app. """
    abstract = True

    user_type = None

    def on_start(self):
        """ Called when a User starts running. """
        self.client.verify = False  # Don't to check if certificate is valid

    # Tasks

    @task
    def open_user_app(self):
        print(f"executing task open_user_app, running on host: {self.host}")
        # ex: https://loadtest-shinyproxy2.staging.serve-dev.scilifelab.se/app/loadtest-shinyproxy2
        # from host: https://staging.serve-dev.scilifelab.se
        APP_SHINYPROXY = self.host.replace("https://", "https://loadtest-shinyproxy2.")
        APP_SHINYPROXY += "/app/loadtest-shinyproxy2"
        print(f"making GET request to URL: {APP_SHINYPROXY}")
        self.client.get(APP_SHINYPROXY, name="user-app-shiny-proxy")



class OpenAPIClientBaseUser(HttpUser):
    """ Base class for API client system that makes API calls. """
    abstract = True

    user_type = None

    def on_start(self):
        self.client.verify = False  # Don't check if certificate is valid
        print(f"ONSTART new user type {self.user_type}")

    # Tasks

    @task
    def call_api_info(self):
        self.client.get("/openapi/v1/api-info")

    @task
    def call_system_version(self):
        self.client.get("/openapi/v1/system-version")

    @task(3)
    def get_public_apps(self):
        self.client.get("/openapi/v1/public-apps")
