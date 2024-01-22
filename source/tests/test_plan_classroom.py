"""Locust test file defining the test plan scenario for the classroom load."""

from locust import between
from base_user_types import VisitingBaseUser, PowerBaseUser, AppViewerUser, OpenAPIClientBaseUser



class VisitingClassroomUser(VisitingBaseUser):
    """ Implements the VisitingBaseUser user type. """

    user_type = "VisitingClassroomUser"
    weight = 2
    wait_time = between(2, 3)


class PowerClassroomUser(PowerBaseUser):
    """ Implements the PowerBaseUser user type. """

    user_type = "PowerClassroomUser"
    weight = 6
    wait_time = between(1, 2)


class AppViewerClassroomUser(AppViewerUser):
    """ Implements the VisitingBaseUser user type. """

    user_type = "AppViewerClassroomUser"
    weight = 1
    wait_time = between(4, 8)


class OpenAPIClientClassroomUser(OpenAPIClientBaseUser):
    """ Implements the ApiBaseUser user type. """

    user_type = "OpenAPIClientClassroomUser"
    weight = 1
    wait_time = between(0.5, 2)
