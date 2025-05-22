from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from account.models import CustomUser
from organization.models import Department


class BaseSetUp(APITestCase):
    """
    Base setup class for initializing test data and utility methods for API tests.
    """

    def setUp(self):
        self.password = "Root@123"  # nosec

        self.admin_user = CustomUser.objects.create_user(
            email="pateldhruvn2004@gmail.com",
            password=self.password,
            role="ADMIN",
            first_name="Dhruv",
            last_name="Patel",
        )

        self.manager_user = CustomUser.objects.create_user(
            email="manager@gmail.com",
            password=self.password,
            role="MANAGER",
            first_name="Aaksh",
            last_name="Senta",
        )

        self.developer_user = CustomUser.objects.create_user(
            email="dev@gmail.com",
            password=self.password,
            role="DEVELOPER",
            first_name="Dev",
            last_name="Loper",
        )

        self.login_url = reverse("login")
        self.user_list_create = reverse("user-list-create")
        # self.user_retrive_update = reverse("user-retrieve-update")
        # self.department_list_create = reverse("department-list-create")
        # self.department_retrieve_update = reverse("department-retrieve-update")

    def login_admin_user(self):
        response = self.client.post(
            self.login_url, {"email": self.admin_user.email, "password": self.password}
        )
        return response.data["access"], response.data["refresh"]


class TestUsers(BaseSetUp):
    """Test suite for user-related API endpoints: list, create, retrieve, and update users."""

    def test_list_all_users_admin(self):
        access, _ = self.login_admin_user()
        response = self.client.get(
            self.user_list_create, HTTP_AUTHORIZATION=f"Bearer {access}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user_admin(self):
        access, _ = self.login_admin_user()
        data = {
            "email": "newuser@gmail.com",
            "password": "Test@123",
            "role": "DEVELOPER",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(
            self.user_list_create, data, HTTP_AUTHORIZATION=f"Bearer {access}"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_user_admin(self):
        access, _ = self.login_admin_user()
        url = reverse(
            "user-retrieve-update", kwargs={"email": self.developer_user.email}
        )
        response = self.client.get(url, HTTP_AUTHORIZATION=f"Bearer {access}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.developer_user.email)

    def test_update_user_admin(self):
        access, _ = self.login_admin_user()
        url = reverse("user-retrieve-update", kwargs={"email": self.manager_user.email})
        data = {"role": "ADMIN"}
        response = self.client.patch(url, data, HTTP_AUTHORIZATION=f"Bearer {access}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role"], "ADMIN")


class TestDepartments(BaseSetUp):

    def setUp(self):
        super().setUp()
        self.department = Department.objects.create(department_name="Engineering")
        self.department_list_create = reverse("department-list-create")
        self.department_retrieve_update = reverse(
            "department-retrieve-update", kwargs={"pk": self.department.pk}
        )

    def test_list_departments_admin(self):
        access, _ = self.login_admin_user()
        response = self.client.get(
            self.department_list_create, HTTP_AUTHORIZATION=f"Bearer {access}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_department_admin(self):
        access, _ = self.login_admin_user()
        data = {"department_name": "Human Resources"}
        response = self.client.post(
            self.department_list_create, data, HTTP_AUTHORIZATION=f"Bearer {access}"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_department_admin(self):
        access, _ = self.login_admin_user()
        response = self.client.get(
            self.department_retrieve_update, HTTP_AUTHORIZATION=f"Bearer {access}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["department_name"], self.department.department_name
        )

    def test_update_department_admin(self):
        access, _ = self.login_admin_user()
        data = {"department_name": "Updated Dept"}
        response = self.client.patch(
            self.department_retrieve_update, data, HTTP_AUTHORIZATION=f"Bearer {access}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["department_name"], "Updated Dept".upper())
