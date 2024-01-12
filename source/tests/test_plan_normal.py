"""Locust test file defining the test plan scenario for normal load."""

from locust import between
from base_user_types import VisitingBaseUser, OpenAPIClientBaseUser



class VisitingNormalUser(VisitingBaseUser):
    """ Implements the VisitingBaseUser user type. """

    user_type = "VisitingNormalUser"
    weight = 6
    wait_time = between(2, 3)


class OpenAPIClientNormalUser(OpenAPIClientBaseUser):
    """ Implements the ApiBaseUser user type. """

    user_type = "ApiNormalUser"
    weight = 1
    wait_time = between(0.5, 2)


# TODO PowerNormalUser: 1
    
# TODO: AppNormalUser: 2
