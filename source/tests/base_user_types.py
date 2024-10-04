import logging
import os
import warnings

from locust import HttpUser, between, task

logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore")


SERVE_LOCUST_TEST_USER_PASS = os.environ.get("SERVE_LOCUST_TEST_USER_PASS")
SERVE_LOCUST_DO_CREATE_OBJECTS = bool(os.environ.get("SERVE_LOCUST_DO_CREATE_OBJECTS", False))


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
        logger.info("ONSTART new user type %s, individual %s", self.user_type, self.local_individual_id)

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
        if not SERVE_LOCUST_DO_CREATE_OBJECTS:
            logger.debug("Skipping register new user because env var SERVE_LOCUST_DO_CREATE_OBJECTS == False")
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
                password1="Ac3ya89ni3wk!",
                password2="Ac3ya89ni3wk!",
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
                logger.debug("signup response.status_code = %s, %s", response.status_code, response.reason)
                # If the signup succeeds then url = /accounts/login/
                logger.debug("signup response.url = %s", response.url)
                if "/accounts/login" in response.url:
                    self.user_has_registered = True
                else:
                    logger.warning(
                        f"Register as new user {self.email} failed. \
                            Response URL {response.url} does not contain /accounts/login"
                    )
                    logger.debug(response.content)
                    response.failure(
                        f"Register as new user {self.email} failed. \
                            Response URL {response.url} does not contain /accounts/login"
                    )

    def get_token(self):
        self.client.get("/signup/")
        self.csrftoken = self.client.cookies["csrftoken"]
        logger.debug("self.csrftoken = %s", self.csrftoken)


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
        logger.info("ONSTART new user type %s, individual %s", self.user_type, self.local_individual_id)
        # Use the pre-created test users for this: f"locust_test_user_{self.local_individual_id}@test.uu.net"
        self.username = f"locust_test_user_{self.local_individual_id}@test.uu.net"
        # self.username = "locust_test_persisted_user@test.uu.net"

    # Tasks

    @task
    def power_user_task(self):
        if self.task_has_run is True:
            logger.debug("Skipping power user task for user %s. It has already been run.", self.local_individual_id)
            return

        self.task_has_run = True

        logger.info("executing power user task")

        # Open the home page
        self.client.get("/home/")

        # Open the login page and get the csrf token
        self.get_token()

        # Login as user locust_test_user_{id}@test.uu.net
        self.login()

        if self.is_authenticated is False:
            logger.info(f"After login function but user {self.username} is not authenticated. Ending task.")
            return

        # Open user docs pages
        self.client.get("/docs/")

        if SERVE_LOCUST_DO_CREATE_OBJECTS is False or SERVE_LOCUST_DO_CREATE_OBJECTS == "False":
            logger.info(
                "Skipping tasks that create and delete projects and apps because env var \
                    SERVE_LOCUST_DO_CREATE_OBJECTS == False"
            )
            return
        else:
            logger.info("Creating and deleting projects and apps as user %s", self.username)

            # Create project: locust_test_project_new_<id>
            project_name = f"locust_test_project_new_{self.local_individual_id}"
            self.create_project(project_name)

            # Open the project
            logger.info("Opening project at URL %s", self.project_url)
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
        logger.debug("self.csrftoken = %s", self.csrftoken)

    def create_project(self, project_name: str):
        # Update the csrf token
        self.get_token("/projects/create/?template=Default project")

        project_data = dict(
            name=project_name,
            template_id=1,
            description="Project desc",
            csrfmiddlewaretoken=self.csrftoken,
        )

        with self.client.post(
            url="/projects/create/?template=Default%20project",
            data=project_data,
            headers={"Referer": "foo"},
            name="---CREATE-NEW-PROJECT",
            catch_response=True,
        ) as response:
            logger.debug("create project response.status_code = %s, %s", response.status_code, response.reason)
            # If succeeds then url = /projects/<project-name>/
            logger.debug("create project response.url = %s", response.url)
            if project_name in response.url:
                logger.info("Successfully created project %s", project_name)
                self.project_url = response.url
            else:
                logger.warning(
                    f"Create project failed. Response URL {response.url} does not contain project name {project_name}"
                )
                # logger.debug(response.content)
                response.failure("Create project failed. Response URL does not contain project name.")

    def delete_project(self):
        # Update the csrf token
        self.get_token("/projects")

        delete_project_url = f"{self.project_url}delete/"  # The project_url already contains a trailing slash
        logger.info("Deleting the project at URL: %s", delete_project_url)

        delete_project_data = dict(csrfmiddlewaretoken=self.csrftoken)

        with self.client.get(
            url=delete_project_url,
            data=delete_project_data,
            headers={"Referer": "foo"},
            name="---DELETE-PROJECT",
            catch_response=True,
        ) as response:
            logger.debug("delete project response.status_code = %s, %s", response.status_code, response.reason)
            # If succeeds then status_code == 200 and url = /projects/
            logger.debug("delete project response.url = %s", response.url)
            if response.status_code == 200 and "/projects" in response.url:
                logger.info("Successfully deleted project at %s", self.project_url)
            else:
                logger.warning(
                    f"Delete project failed for project {self.project_url}. \
                        Response status not 200 or URL does not contain /projects."
                )
                # logger.debug(response.content)
                response.failure("Delete project failed. Response URL does not contain /projects.")

    def login(self):
        logger.info("Login as user %s", self.username)

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
            logger.debug("login response.status_code = %s, %s", response.status_code, response.reason)
            # If login succeeds then the url contains /projects/, else /accounts/login/
            logger.debug("login response.url = %s", response.url)
            if "/projects" in response.url:
                self.is_authenticated = True
            else:
                logger.warning(
                    f"Login as user {self.username} failed. Response URL {response.url} does not contain /projects"
                )
                response.failure(f"Login as user {self.username} failed. Response URL does not contain /projects")

    def logout(self):
        if self.is_authenticated:
            logger.debug("Logout user %s", self.username)
            logout_data = dict(username=self.username, csrfmiddlewaretoken=self.csrftoken)
            with self.client.post(
                "/accounts/logout/",
                data=logout_data,
                headers={"Referer": "foo"},
                name="---ON STOP---LOGOUT",
                catch_response=True,
            ):
                pass


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
        logger.info("executing task open_user_app, running on host: %s", self.host)

        APP_SHINYPROXY = "UNSET"

        if self.host == "https://serve-dev.scilifelab.se":
            # Dev
            # ex: https://loadtest-shinyproxy.serve-dev.scilifelab.se/app/loadtest-shinyproxy
            # from host: https://serve-dev.scilifelab.se
            APP_SHINYPROXY = self.host.replace("https://", "https://loadtest-shinyproxy.")
            APP_SHINYPROXY += "/app/loadtest-shinyproxy"

        elif "staging" in self.host:
            # Staging
            # ex: https://loadtest-shinyproxy.serve-staging.serve-dev.scilifelab.se/app/loadtest-shinyproxy
            # from host: https://serve-staging.serve-dev.scilifelab.se
            APP_SHINYPROXY = self.host.replace("https://", "https://loadtest-shinyproxy.")
            APP_SHINYPROXY += "/app/loadtest-shinyproxy"

        elif "serve.scilifelab.se" in self.host:
            # Production
            # ex: https://adhd-medication-sweden.serve.scilifelab.se/app/adhd-medication-sweden
            APP_SHINYPROXY = self.host.replace("https://", "https://adhd-medication-sweden.")
            APP_SHINYPROXY += "/app/adhd-medication-sweden"

        logger.debug("making GET request to user app URL: %s", APP_SHINYPROXY)

        self.client.get(APP_SHINYPROXY, name="user-app-shiny-proxy")


class OpenAPIClientBaseUser(HttpUser):
    """Base class for API client system that makes API calls."""

    abstract = True

    user_type = ""

    def on_start(self):
        self.client.verify = False  # Don't check if certificate is valid
        logger.info("ONSTART new user type %s", self.user_type)

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
