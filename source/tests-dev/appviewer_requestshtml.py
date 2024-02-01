"""
Handles opening user apps.
This implementation does not use Locust and does not work with Locust.

Note that shiny proxy pods are configured with
- heartbeat-rate=10s
- heartbeat-timeout=60s
"""

from time import time, sleep
import requests
from requests_html import HTMLSession
import warnings
warnings.filterwarnings("ignore")


# SETTINGS

# The user app URLs to open in succession
URL_LIST = [
    #"https://loadtest-shinyproxy.serve-dev.scilifelab.se/app/loadtest-shinyproxy"
    "https://loadtest-shinyproxy2.staging.serve-dev.scilifelab.se/app/loadtest-shinyproxy2"
    #"https://demo-bayesianlinmod.serve.scilifelab.se/app/demo-bayesianlinmod",
    #"https://demo-markovchain.serve.scilifelab.se/app/demo-markovchain"
]

# The maximum number of apps are allowed to be opened
MAX_APPS_PER_APP_TYPE_LIMIT = 20

# The initial delay to wait before opening any user apps
INITIAL_DELAY_SECONDS = 10

# The amount of time to wait between opening up each consecutive user app type
DELAY_BETWEEN_USER_APP_TYPES_SECONDS = 10

# The wait time between opening user apps of the same app type
OPEN_APPS_WAIT_TIME_SECONDS = 2



def apps_runner(n_requests: int = 1):
    """ Opens user apps.
        This results in pods created.
        :param n_requests int: The number of instances of each app to be opened.
    """

    if n_requests > MAX_APPS_PER_APP_TYPE_LIMIT:
        raise Exception(f"Too many instances of user apps requested to be opened. Max = {MAX_APPS_PER_APP_TYPE_LIMIT}")

    start_time = time()
    n_fails = 0

    sleep(INITIAL_DELAY_SECONDS)
    print("START apps_runner")

    for url in URL_LIST:
        print(f"AppViewer URL set to: {url}")
        for i in range(1,n_requests+1):
            print(f"Iteration: {i}")
            try:
                response = open_user_app_sync(url)
                print(f"DEBUG: open_user_app_sync response = {response.status_code}, {response.reason}")
                #print(response.content)
            except Exception as ex:
                n_fails += 1
                print(f"Error while opening a user app {ex}")

            sleep(OPEN_APPS_WAIT_TIME_SECONDS)

        sleep(DELAY_BETWEEN_USER_APP_TYPES_SECONDS)

    duration_s = time() - start_time
    print(f"Duration (sec) for opening {n_requests} user apps = {duration_s}. Nr failures = {n_fails}")


def open_user_app_sync(url: str):
    """
        Opens a user app that requires js support as an anonymous user.
        This results in a pod created on k8s when run via module.
        :param url: The app URL.
    """
    print(f"DEBUG: Making a GET request to url {url}")
    session = HTMLSession(verify=False)
    r = session.get(url)
    assert r.status_code == 200
    r.html.render()
    return r




# Private functions

def __test_open_sync(n_requests):
    apps_runner(n_requests)



if __name__ == "__main__":
    print("Begin running appviewer_requestshtml.py")
    apps_runner(4)
    print("Completed running appviewer_requestshtml.py")
