"""
Handles opening user apps.
This implementation does not use Locust and does not work through Locust.
It can however be run concurrently with Locust load tests to put additional
realistic load on the system.

Note that shiny proxy pods are configured with
- heartbeat-rate=10s
- heartbeat-timeout=60s
"""

import logging
import warnings
from time import sleep, time

from requests_html import HTMLSession

logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore")


# SETTINGS

# The user app URLs to open in succession
URL_LIST = [
    "https://loadtest-shinyproxy.serve-dev.scilifelab.se/app/loadtest-shinyproxy"
    # "https://loadtest-shinyproxy.serve-staging.serve-dev.scilifelab.se/app/loadtest-shinyproxy"
    # "https://demo-bayesianlinmod.serve.scilifelab.se/app/demo-bayesianlinmod",
    # "https://demo-markovchain.serve.scilifelab.se/app/demo-markovchain"
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
    """
    Opens user apps.
        This results in pods created.

        :param n_requests int: The number of instances of each app to be opened.
    """

    if n_requests > MAX_APPS_PER_APP_TYPE_LIMIT:
        raise Exception(f"Too many instances of user apps requested to be opened. Max = {MAX_APPS_PER_APP_TYPE_LIMIT}")

    start_time = time()
    n_fails = 0

    sleep(INITIAL_DELAY_SECONDS)
    logger.info("START apps_runner")

    for url in URL_LIST:
        logger.info("AppViewer URL set to: %s", url)

        for i in range(1, n_requests + 1):
            logger.debug("Iteration: %s", i)
            try:
                response = open_user_app_sync(url)
                logger.debug("open_user_app_sync response = %s, %s", response.status_code, response.reason)
                logger.debug(response.content)

            except Exception as ex:
                n_fails += 1
                logger.warning("Unable to open a user app. Error: %s", ex)

            sleep(OPEN_APPS_WAIT_TIME_SECONDS)

        sleep(DELAY_BETWEEN_USER_APP_TYPES_SECONDS)

    duration_s = time() - start_time
    logger.info("Duration (sec) for opening %s user apps = %s. Nr failures = %s", n_requests, duration_s, n_fails)


def open_user_app_sync(url: str):
    """
    Opens a user app that requires js support as an anonymous user.
    This results in a pod created on k8s when run via module.
    :param url: The app URL.
    """

    logger.info("Making a GET request to url: %s", url)

    session = HTMLSession(verify=False)
    r = session.get(url)
    assert r.status_code == 200
    r.html.render()
    return r


# Private functions


def __test_open_sync(n_requests):
    apps_runner(n_requests)


if __name__ == "__main__":
    loglevel = logging.getLevelName(logger.getEffectiveLevel())
    print(f"Begin running appviewer_requestshtml.py using logging level {loglevel}")
    apps_runner(4)
    print("Completed running appviewer_requestshtml.py")
