"""Locust test file defining the test plan scenario for the classroom load."""

from locust import between
from base_user_types import VisitingBaseUser, PowerBaseUser, AppViewerUser, OpenAPIClientBaseUser



class PowerClassroomUser(PowerBaseUser):
    """ Implements the PowerBaseUser user type. """

    user_type = "PowerClassroomUser"
    weight = 1
    wait_time = between(1, 2)
