"""Locust test file defining the test plan scenario for the classroom load."""

from base_user_types import AppViewerUser, PowerBaseUser, VisitingBaseUser
from locust import between


class VisitingClassroomUser(VisitingBaseUser):
    """Implements the VisitingBaseUser user type."""

    user_type = "VisitingClassroomUser"
    weight = 2
    wait_time = between(2, 3)


class StudentClassroomUser(PowerBaseUser):
    """Implements the PowerBaseUser user type as a Student type user."""

    is_student_user = True

    user_type = "StudentClassroomUser"
    weight = 7
    wait_time = between(2, 3)


class AppViewerClassroomUser(AppViewerUser):
    """Implements the VisitingBaseUser user type."""

    user_type = "AppViewerClassroomUser"
    weight = 1
    wait_time = between(4, 8)
