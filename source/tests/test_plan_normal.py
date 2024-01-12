"""Locust test file defining the test plan scenario for normal load."""

from locust import between
from base_user_types import VisitingBaseUser, AppViewerUser, OpenAPIClientBaseUser



class VisitingNormalUser(VisitingBaseUser):
    """ Implements the VisitingBaseUser user type. """

    user_type = "VisitingNormalUser"
    weight = 6
    wait_time = between(2, 3)


# TODO PowerNormalUser: 1
    

class AppViewerNormalUser(AppViewerUser):
    """ Implements the VisitingBaseUser user type. """

    user_type = "AppViewerNormalUser"
    weight = 2
    wait_time = between(4, 8)


class OpenAPIClientNormalUser(OpenAPIClientBaseUser):
    """ Implements the ApiBaseUser user type. """

    user_type = "OpenAPIClientNormalUser"
    weight = 1
    wait_time = between(0.5, 2)
