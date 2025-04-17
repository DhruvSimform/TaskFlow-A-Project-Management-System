from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class LoginThrottlePerMinute(AnonRateThrottle):
    """Throttle class for limiting login attempts per minute."""

    scope = "login_min"


class LoginThrottlePerHour(AnonRateThrottle):
    """Throttle class for limiting login attempts per hour."""

    scope = "login_hour"


class RefreshTokenThrottle(AnonRateThrottle):
    """
    Throttle class for limiting refresh token requests.
    """

    scope = "refresh"


class ChangePasswordThrottle(UserRateThrottle):
    """
    Throttle class for limiting change password requests.
    """

    scope = "change_password"
    # def allow_request(self, request, view):
    #     return super().allow_request(request, view)


class ResetPasswordThrottle(AnonRateThrottle):
    """
    Throttle class for limiting reset password requests.
    """

    scope = "reset_password"
