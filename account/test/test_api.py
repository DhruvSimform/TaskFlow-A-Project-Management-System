from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from account.models import CustomUser


class BaseAuthTest(APITestCase):
    def setUp(self):

        self.password = "Root@123"  # nosec
        self.user = CustomUser.objects.create_user(
            email="pateldhruvn2004@gmail.com",
            password=self.password,
            role="ADMIN",
            first_name="Dhruv",
            last_name="Patel",
        )
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.refresh_url = reverse("token_refresh")
        self.change_password_url = reverse("change_password")
        self.home_url = reverse("home")

    def login_user(self):
        response = self.client.post(
            self.login_url, {"email": self.user.email, "password": self.password}
        )
        return response.data["access"], response.data["refresh"]


class TestLogin(BaseAuthTest):

    def test_successful_login_returns_tokens(self):
        response = self.client.post(
            self.login_url, {"email": self.user.email, "password": self.password}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_invalid_password_returns_unauthorized(self):
        response = self.client.post(
            self.login_url, {"email": self.user.email, "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_email_returns_bad_request(self):
        response = self.client.post(self.login_url, {"password": self.password})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_disallowed_methods_on_login(self):
        for method in ["get", "put", "patch", "delete"]:
            response = getattr(self.client, method)(self.login_url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class TestLogoutFlow(BaseAuthTest):

    def test_logout_successful(self):
        access, refresh = self.login_user()
        response = self.client.post(
            self.logout_url,
            data={"refresh": refresh},
            HTTP_AUTHORIZATION=f"Bearer {access}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_without_token(self):
        _, refresh = self.login_user()
        response = self.client.post(self.logout_url, data={"refresh": refresh})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_with_invalid_token(self):
        _, refresh = self.login_user()
        response = self.client.post(
            self.logout_url,
            data={"refresh": refresh},
            HTTP_AUTHORIZATION="Bearer invalidtoken",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_token_blacklisted_after_logout(self):
        access, refresh = self.login_user()
        self.client.post(
            self.logout_url,
            data={"refresh": refresh},
            HTTP_AUTHORIZATION=f"Bearer {access}",
        )
        response = self.client.get(self.home_url, HTTP_AUTHORIZATION=f"Bearer {access}")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_disallowed_methods_on_logout(self):
        access, refresh = self.login_user()
        for method in ["get", "put", "patch", "delete"]:
            response = getattr(self.client, method)(
                self.logout_url,
                HTTP_AUTHORIZATION=f"Bearer {access}",
            )
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class TestTokenRefresh(BaseAuthTest):

    def test_refresh_token_success(self):
        _, refresh = self.login_user()
        response = self.client.post(self.refresh_url, data={"refresh": refresh})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_blacklisted_refresh_token_fails(self):
        access, refresh = self.login_user()
        self.client.post(
            self.logout_url,
            data={"refresh": refresh},
            HTTP_AUTHORIZATION=f"Bearer {access}",
        )
        response = self.client.post(self.refresh_url, data={"refresh": refresh})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_disallowed_methods_on_token_refresh(self):
        access, refresh = self.login_user()
        for method in ["get", "put", "patch", "delete"]:
            response = getattr(self.client, method)(self.refresh_url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class TestPasswordChange(BaseAuthTest):

    def test_password_change_success(self):
        access, _ = self.login_user()
        response = self.client.put(
            self.change_password_url,
            data={"new_password": "New@1234"},
            HTTP_AUTHORIZATION=f"Bearer {access}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_change_unauthenticated(self):
        response = self.client.put(
            self.change_password_url,
            data={"new_password": "New@1234"},
            HTTP_AUTHORIZATION="Bearer dfdfda5f75f78",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_disallowed_methods_on_password_change(self):
        access, refresh = self.login_user()
        for method in ["get", "post", "delete"]:
            response = getattr(self.client, method)(
                self.change_password_url,
                HTTP_AUTHORIZATION=f"Bearer {access}",
            )
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
