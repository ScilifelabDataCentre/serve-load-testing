import logging
import warnings

from locust import HttpUser, task

logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore")


class VisitingBaseUser(HttpUser):
    """Base class for a visiting website user type that may also register a new user account in Serve.
    Simulates a casual, visiting, non-authenticated user that browses the public pages.
    Some of these users may register new user accounts, using emails with pattern:
        locust_test_user_created_by_testrun_{i}@test.uu.net
    """

    # abstract = True

    user_type = ""
    user_individual_id = 0
    local_individual_id = 0
    user_has_registered = False

    @classmethod
    def get_user_id(cls):
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
        self.email = "UNSET"

    # Tasks

    @task
    def browse_homepage(self):
        self.client.get("/home/")

    @task
    def register_user(self):
        """Register this user as a new user account."""
        if self.user_has_registered is False:
            # Only attempt to register once
            self.user_has_registered = True

            self.email = f"locust_test_user_created_by_testrun_{self.local_individual_id}@test.uu.net"
            logger.info("Registering new user account using email %s", self.email)

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
                logger.debug("signup response.status_code = %s, %s", response.status_code, response.reason)
                # If login succeeds then url = /accounts/login/
                logger.debug("signup response.url = %s", response.url)
                if "/accounts/login" in response.url:
                    self.user_has_registered = True
                else:
                    logger.info(response.content)
                    response.failure(
                        f"Register as new user {self.email} failed. Response URL does not contain /accounts/login"
                    )

    def get_token(self):
        self.client.get("/signup/")
        self.csrftoken = self.client.cookies["csrftoken"]
        logger.debug("self.csrftoken = %s", self.csrftoken)
