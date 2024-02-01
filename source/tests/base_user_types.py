import os
import warnings

from locust import HttpUser, between, task

warnings.filterwarnings("ignore")


SERVE_LOCUST_TEST_USER_PASS = os.environ.get("SERVE_LOCUST_TEST_USER_PASS")
SERVE_LOCUST_DO_CREATE_OBJECTS = os.environ.get("SERVE_LOCUST_DO_CREATE_OBJECTS", "False")


class VisitingBaseUser(HttpUser):
    """Base class for a visiting website user type that may also register a new user account in Serve.
    Simulates a casual, visiting, non-authenticated user that browses the public pages.
    Some of these users may register new user accounts, using emails with pattern:
        locust_test_user_created_by_testrun_{i}@test.uu.net
    """

    abstract = True

    user_type = ""
    user_individual_id = 0
    local_individual_id = 0
    user_has_registered = False

    @classmethod
    def get_user_id(cls) -> int:
        """Increments the class property user_individual_id.
        Used to assign a unique id to each individual of this user type.
        """
        VisitingBaseUser.user_individual_id += 1
        return VisitingBaseUser.user_individual_id

    def on_start(self):
        """Called when a User starts running."""
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

    @task
    def register_user(self):
        """Register this user as a new user account."""
        if SERVE_LOCUST_DO_CREATE_OBJECTS is False or SERVE_LOCUST_DO_CREATE_OBJECTS == "False":
            print("Skipping register new user because env var SERVE_LOCUST_DO_CREATE_OBJECTS == False")
            return

        if self.user_has_registered is False:
            # Only attempt to register once
            self.user_has_registered = True

            self.email = f"locust_test_user_created_by_testrun_{self.local_individual_id}@test.uu.net"
            print(f"Registering new user account using email {self.email}")

            self.get_token()

            register_data = dict(
                email=self.email,
                why_account_needed="For load testing",
                first_name="Delete",
                last_name="Me",
                affiliation="other",
                department="Dept ABC",
                password1="ac3ya89ni3wk",
                password2="ac3ya89ni3wk",
                note="",
                csrfmiddlewaretoken=self.csrftoken,
            )

            with self.client.post(
                url="/signup/",
                data=register_data,
                headers={"Referer": "foo"},
                name="---REGISTER-NEW-USER-ACCOUNT",
                catch_response=True,
            ) as response:
                print(f"DEBUG: signup response.status_code = {response.status_code}, {response.reason}")
                # if login succeeds then url = /accounts/login/
                print(f"DEBUG: signup response.url = {response.url}")
                if "/accounts/login" in response.url:
                    self.user_has_registered = True
                else:
                    print(response.content)
                    response.failure(
                        f"Register as new user {self.email} failed. Response URL does not contain /accounts/login"
                    )

    def get_token(self):
        self.client.get("/signup/")
        self.csrftoken = self.client.cookies["csrftoken"]
        print(f"DEBUG: self.csrftoken = {self.csrftoken}")


class PowerBaseUser(HttpUser):
    """Base class for the power user type that logs into Serve using an existing user account,
    then creates resources such as a project and app and finally deleted the app.
    """

    abstract = True

    user_type = ""
    user_individual_id = 0
    local_individual_id = 0

    username = "NOT_FOUND"
    password = SERVE_LOCUST_TEST_USER_PASS

    project_url = "UNSET"

    is_authenticated = False
    task_has_run = False

    @classmethod
    def get_user_id(cls) -> int:
        """Increments the class property user_individual_id.
        Used to assign a unique id to each individual of this user type.
        """
        PowerBaseUser.user_individual_id += 1
        return PowerBaseUser.user_individual_id

    def on_start(self):
        """Called when a User starts running."""
        self.client.verify = False  # Don't check if certificate is valid
        self.local_individual_id = PowerBaseUser.get_user_id()
        print(f"ONSTART new user type {self.user_type}, individual {self.local_individual_id}")
        # Use the pre-created test users for this: f"locust_test_user_{self.local_individual_id}@test.uu.net"
        self.username = f"locust_test_user_{self.local_individual_id}@test.uu.net"
        # self.username = "locust_test_persisted_user@test.uu.net"

    # Tasks

    @task
    def power_user_task(self):
        if self.task_has_run is True:
            print(f"Skipping power user task for user {self.local_individual_id}. It has already been run.")
            return

        self.task_has_run = True

        print("executing power user task")

        # Open the home page
        self.client.get("/home/")

        # Open the login page and get the csrf token
        self.get_token()

        # Login as user locust_test_user_{id}@test.uu.net
        self.login()

        if self.is_authenticated is False:
            return

        # Open user docs pages
        self.client.get("/docs/")

        if SERVE_LOCUST_DO_CREATE_OBJECTS is False or SERVE_LOCUST_DO_CREATE_OBJECTS == "False":
            print(
                "Skipping tasks that create and delete projects and apps because env var \
                    SERVE_LOCUST_DO_CREATE_OBJECTS == False"
            )
            return
        else:
            print(f"DEBUG: Creating and deleting projects and apps as user {self.username}")

            # Create project: locust_test_project_new_<id>
            project_name = f"locust_test_project_new_{self.local_individual_id}"
            self.create_project(project_name)

            # Open the project
            print(f"Opening project at URL {self.project_url}")
            self.client.get(self.project_url)

            # TODO: create JupyterLab app

            # TODO: open the app

            # TODO: delete the app

            # Delete the project
            self.delete_project()

        # Logout the user
        self.logout()

    def get_token(self, relative_url: str = "/accounts/login/"):
        self.client.get(relative_url)
        self.csrftoken = self.client.cookies["csrftoken"]
        print(f"DEBUG: self.csrftoken = {self.csrftoken}")

    def create_project(self, project_name: str):
        # Update the csrf token
        self.get_token("/projects/create?template=Default project")

        project_data = dict(
            name=project_name,
            template_id=1,
            description="Project desc",
            csrfmiddlewaretoken=self.csrftoken,
        )

        with self.client.post(
            url="/projects/create?template=Default%20project",
            data=project_data,
            headers={"Referer": "foo"},
            name="---CREATE-NEW-PROJECT",
            catch_response=True,
        ) as response:
            print(f"DEBUG: create project response.status_code = {response.status_code}, {response.reason}")
            # if succeeds then url = /<username>/<project-name>
            print(f"DEBUG: create project response.url = {response.url}")
            if self.username in response.url and project_name in response.url:
                print(f"Successfully created project {project_name}")
                self.project_url = response.url
            else:
                print(response.content)
                response.failure("Create project failed. Response URL does not contain username and project name.")

    def delete_project(self):
        # Update the csrf token
        self.get_token("/projects")

        delete_project_url = f"{self.project_url}/delete"
        print(f"DEBUG: Deleting the project at URL: {delete_project_url}")

        delete_project_data = dict(csrfmiddlewaretoken=self.csrftoken)

        with self.client.get(
            url=delete_project_url,
            data=delete_project_data,
            headers={"Referer": "foo"},
            name="---DELETE-PROJECT",
            catch_response=True,
        ) as response:
            print(f"DEBUG: delete project response.status_code = {response.status_code}, {response.reason}")
            # if succeeds then url = /projects/
            print(f"DEBUG: delete project response.url = {response.url}")
            if "/projects" in response.url:
                print(f"Successfully deleted project at {self.project_url}")
            else:
                print(response.content)
                response.failure("Delete project failed. Response URL does not contain /projects.")

    def login(self):
        print(f"DEBUG: Login as user {self.username}")

        login_data = dict(
            username=self.username,
            password=self.password,
            csrfmiddlewaretoken=self.csrftoken,
        )

        with self.client.post(
            url="/accounts/login/",
            data=login_data,
            headers={"Referer": "foo"},
            name="---ON START---LOGIN",
            catch_response=True,
        ) as response:
            print(f"DEBUG: login response.status_code = {response.status_code}, {response.reason}")
            # if login succeeds then url = /accounts/login/, else /projects/
            print(f"DEBUG: login response.url = {response.url}")
            if "/projects" in response.url:
                self.is_authenticated = True
            else:
                response.failure(f"Login as user {self.username} failed. Response URL does not contain /projects")

    def logout(self):
        print(f"DEBUG: Login out user {self.username}")
        # logout_data = dict(username=self.username, csrfmiddlewaretoken=self.csrftoken)
        self.client.get("/accounts/logout/", name="---ON STOP---LOGOUT")


class AppViewerUser(HttpUser):
    """Base class for app viewer user that opens up a user app."""

    abstract = True

    user_type = ""

    def on_start(self):
        """Called when a User starts running."""
        self.client.verify = False  # Don't to check if certificate is valid

    # Tasks

    @task
    def open_user_app(self):
        """Note that this approach does not actually create any resources on the k8s cluster."""
        print(f"executing task open_user_app, running on host: {self.host}")
        APP_SHINYPROXY = "UNSET"
        if self.host == "https://serve-dev.scilifelab.se":
            # Dev
            # ex: https://loadtest-shinyproxy.staging.serve-dev.scilifelab.se/app/loadtest-shinyproxy
            # from host: https://staging.serve-dev.scilifelab.se
            APP_SHINYPROXY = self.host.replace("https://", "https://loadtest-shinyproxy.")
            APP_SHINYPROXY += "/app/loadtest-shinyproxy"
        elif "staging" in self.host:
            # Staging
            # ex: https://loadtest-shinyproxy2.staging.serve-dev.scilifelab.se/app/loadtest-shinyproxy2
            # from host: https://staging.serve-dev.scilifelab.se
            APP_SHINYPROXY = self.host.replace("https://", "https://loadtest-shinyproxy2.")
            APP_SHINYPROXY += "/app/loadtest-shinyproxy2"
        elif "serve.scilifelab.se" in self.host:
            # Production
            # ex: https://adhd-medication-sweden.serve.scilifelab.se/app/adhd-medication-sweden
            APP_SHINYPROXY = self.host.replace("https://", "https://adhd-medication-sweden.")
            APP_SHINYPROXY += "/app/adhd-medication-sweden"

        print(f"making GET request to URL: {APP_SHINYPROXY}")
        self.client.get(APP_SHINYPROXY, name="user-app-shiny-proxy")


class OpenAPIClientBaseUser(HttpUser):
    """Base class for API client system that makes API calls."""

    abstract = True

    user_type = ""

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
