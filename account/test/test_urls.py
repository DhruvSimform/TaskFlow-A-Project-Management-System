# from django.urls import reverse, resolve
# from rest_framework.test import APITestCase
# from account.views import (
#     CustomTokenRefreshView,
#     LogoutView,
#     ChangePasswordView,
#     Home,
# )
# from rest_framework_simplejwt.views import TokenObtainPairView

# class URLResolutionTests(APITestCase):
#     def test_token_refresh_url(self):
#         url = reverse("token_refresh")  # or your actual name
#         resolver = resolve(url)
#         self.assertEqual(resolver.func.view_class, CustomTokenRefreshView)

#     def test_logout_url(self):
#         url = reverse("logout")
#         resolver = resolve(url)
#         self.assertEqual(resolver.func.view_class, LogoutView)

#     def test_login_url(self):
#         url=reverse("login")
#         resolver = resolve(url)

#         self.assertEqual(resolver.func.view_class,TokenObtainPairView)

#     def test_change_password_url(self):
#         url = reverse("change_password")
#         resolver = resolve(url)
#         self.assertEqual(resolver.func.view_class, ChangePasswordView)

#     def test_home_url(self):
#         url = reverse("home")
#         resolver = resolve(url)
#         self.assertEqual(resolver.func.view_class, Home)
