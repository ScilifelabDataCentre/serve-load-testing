import logging
import os
import time
import warnings

from locust import HttpUser, between, task
from lxml import etree
from requests_html import HTML, AsyncHTMLSession

# import asyncio
# from io import StringIO
# import requests

logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore")

username = os.environ.get("SERVE_USERNAME")
password = os.environ.get("SERVE_PASS")


# Utility functions
def make_url(url: str):
    """Ensures that the URL contains exactly one trailing slash."""
    return url.rstrip("/") + "/"


class CreatingUser(HttpUser):
    """Simulates an authenticated, power user that creates a project and app."""

    # For now only supports one fixed user
    fixed_count = 1

    wait_time = between(2, 3)

    project_url = "UNSET"

    is_authenticated = False
    task_has_run = False

    def on_start(self):
        logger.debug("on start")
        self.client.verify = False  # Don't check if certificate is valid
        self.get_token()
        self.login()

    # Tasks

    @task
    def create_task(self):
        if self.task_has_run is True:
            logger.debug("Skipping create task for user %s. It has already been run.", username)
            return

        self.task_has_run = True

        logger.info("executing create task")

        # The user should already be logged in
        if self.is_authenticated is False:
            logger.warning(f"The user {self.username} is not authenticated but should be. Ending task.")
            return

        # Create a project
        logger.info("Creating projects and apps as user %s", username)
        project_name = "locust-appcreator-project-" + time.strftime("%Y%m%d-%H%M%S")
        self.create_project(project_name)

        # Open the project
        logger.info("Opening project at URL %s", self.project_url)
        self.client.get(self.project_url)

        # Create an app
        app_name = "locust-jupyterlab-app"
        self._create_app(project_name, app_name)

        # Successful POST is redirected to the projects page

    def _create_app(self, project_name: str, app_name: str):
        # Update the csrf token
        app_create_url = self.project_url + "apps/create/jupyter-lab?from=overview"
        logger.info(f"Using this URL to create a JL notebook app: {app_create_url}")
        self.get_token(app_create_url)

        # Fetch the web page content
        # response = requests.get(app_create_url, data=dict(csrfmiddlewaretoken=self.csrftoken))
        # response = requests.post(app_create_url, data=dict(csrfmiddlewaretoken=self.csrftoken))

        # First make a dummy POST to the form to get the html and parse out the select option values
        app_data = dict(csrfmiddlewaretoken=self.csrftoken)

        html_content = ""
        with self.client.post(
            url=app_create_url,
            data=app_data,
            headers={"Referer": "foo"},
            name="---CREATE-NEW-APP-JUPYTERLAB",
            catch_response=True,
        ) as response:
            logger.debug("create JupyterLab app response.status_code = %s, %s", response.status_code, response.reason)
            html_content = response.content

        # Parse the HTML content
        parser = etree.HTMLParser()
        tree = etree.fromstring(html_content, parser)

        # Must first get the volume, flavor, and environment values from the form
        volume = None
        flavor = None
        environment = None

        # Extract the form values of the option elements using XPath
        # Flavor: <select name="flavor" class="form-control" rows="3" id="id_flavor">
        # <option value="28" selected>2 vCPU, 4 GB RAM</option></select>
        el_volume = tree.xpath('//select[@name="volume"]/option')
        el_flavor = tree.xpath('//select[@name="flavor"]/option')
        el_environment = tree.xpath('//select[@name="environment"]/option')

        if el_volume:
            volume = el_volume[0].get("value")
        else:
            print("Option element VOLUME not found")

        if el_flavor:
            flavor = el_flavor[0].get("value")
        else:
            print("Option element FLAVOR not found")

        if el_environment:
            environment = el_environment[0].get("value")
        else:
            print("Option element ENVIRONMENT not found")

        print(f"The parsed form values to use are: volume={volume}, flavor={flavor}, environment={environment}")

        # To create the app, perform a POST submit to a URL with pattern:
        # https://serve-dev.scilifelab.se/projects/locust-appcreator-project-20241007-145428-sib/apps/create/jupyter-lab?from=overview

        # sesn = requests_html.HTMLSession(verify=False)
        # resp = sesn.get(app_create_url)
        # assert resp.status_code == 200

        # Render JavaScript
        # resp.html.render()

        # Parse the HTML content
        # html = HTML(html=html_raw)

        # Find the option element and extract its value
        # Downloads Chromium
        # from  https://storage.googleapis.com/chromium-browser-snapshots/Linux_x64/1181205/chrome-linux.zip
        # asyncio.run(fetch_and_render(app_create_url))

        app_data = dict(
            name=app_name,
            volume=volume,
            access="project",
            flavor=flavor,
            environment=environment,
            description="Project desc",
            csrfmiddlewaretoken=self.csrftoken,
        )

        with self.client.post(
            url=app_create_url,
            data=app_data,
            headers={"Referer": "foo"},
            name="---CREATE-NEW-APP-JUPYTERLAB",
            catch_response=True,
        ) as response:
            logger.debug("create JupyterLab app response.status_code = %s, %s", response.status_code, response.reason)
            # If succeeds then url = /projects/<project-name>/
            logger.debug("create JupyterLab app response.url = %s", response.url)
            if project_name in response.url and "create/jupyter-lab" not in response.url:
                # The returned URL should NOT be back at the create app page
                logger.info("Successfully created JupyterLab app %s", app_name)
            else:
                logger.warning(f"Create JupyterLab app failed. Response URL {response.url} does not indicate success.")
                logger.debug(response.content)
                response.failure("Create JupyterLab app failed. Response URL does not indicate success.")

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
                self.project_url = make_url(response.url)
            else:
                logger.warning(
                    f"Create project failed. Response URL {response.url} does not contain project name {project_name}"
                )
                # logger.debug(response.content)
                response.failure("Create project failed. Response URL does not contain project name.")

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
        if self.is_authenticated:
            logger.debug("Logout user %s", username)
            logout_data = dict(username=username, csrfmiddlewaretoken=self.csrftoken)
            with self.client.post(
                "/accounts/logout/",
                data=logout_data,
                headers={"Referer": "foo"},
                name="---ON STOP---LOGOUT",
                catch_response=True,
            ):
                pass

    def get_token(self, relative_url: str = "/accounts/login/"):
        self.client.get(relative_url)
        self.csrftoken = self.client.cookies["csrftoken"]
        logger.debug("self.csrftoken = %s", self.csrftoken)

    def on_stop(self):
        logger.debug("on stop. exec logout.")
        self.logout()


# This method is not completed and not used
async def fetch_and_render(url):
    """Fetches the html from a dynamic web page so that it can be parsed.
    This however requires downloading of the Chromium browser."""

    # Create an asynchronous session
    session = AsyncHTMLSession()
    response = await session.get(url)

    # Render JavaScript
    await response.html.arender()

    # Parse the HTML content
    html = response.html

    # Find the option element and extract its value
    option_element = html.find('select[name="flavor"] option[selected]', first=True)
    if option_element:
        option_value = option_element.attrs["value"]
        print(f"Option value: {option_value}")
    else:
        print("Option element not found")

    await session.close()
