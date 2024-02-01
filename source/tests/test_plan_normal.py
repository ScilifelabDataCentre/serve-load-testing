"""Locust test file defining the test plan scenario for normal load."""

from base_user_types import (
    AppViewerUser,
    OpenAPIClientBaseUser,
    PowerBaseUser,
    VisitingBaseUser,
)
from locust import between


class VisitingNormalUser(VisitingBaseUser):
    """Implements the VisitingBaseUser user type."""

    user_type = "VisitingNormalUser"
    weight = 6
    wait_time = between(2, 3)


class PowerNormalUser(PowerBaseUser):
    """Implements the PowerBaseUser user type."""

    user_type = "PowerNormalUser"
    weight = 1
    wait_time = between(1, 2)


class AppViewerNormalUser(AppViewerUser):
    """Implements the VisitingBaseUser user type."""

    user_type = "AppViewerNormalUser"
    weight = 2
    wait_time = between(4, 8)


class OpenAPIClientNormalUser(OpenAPIClientBaseUser):
    """Implements the ApiBaseUser user type."""

    user_type = "OpenAPIClientNormalUser"
    weight = 1
    wait_time = between(0.5, 2)
