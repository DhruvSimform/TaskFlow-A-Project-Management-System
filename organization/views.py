from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView

# Create your views here.
from account.models import CustomUser

from .models import Department
from .permitions import IsAdminUser
from .serializers import DepartmentSerializer, UserRegistrationSerializer
from .services import create_department


class UserView(CreateAPIView, ListAPIView):
    """
    User View for managing user-related operations.

    This view allows administrators to create new users and retrieve a list of all existing users.
    It uses the `UserRegistrationSerializer` for data validation and serialization.
    """

    permission_classes = [IsAdminUser]
    lookup_field = "email"
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer


class UserUpdateRetriveView(RetrieveUpdateAPIView):
    """
    User Update and Retrieve View for managing user-related operations.

    This view allows administrators to retrieve and update details of existing users.
    It uses the `UserRegistrationSerializer` for data validation and serialization.
    """

    permission_classes = [IsAdminUser]
    lookup_field = "email"
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer


class DepartmentView(CreateAPIView, ListAPIView):
    """
    Department View for managing department-related operations.

    This view allows administrators to create new departments and retrieve a list of all existing departments.
    It uses the `DepartmentSerializer` for data validation and serialization.
    """

    permission_classes = [IsAdminUser]
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()

    def perform_create(self, serializer):
        create_department(serializer.validated_data, self.request.user)


class DepartmentUpdateRetriveView(RetrieveUpdateAPIView):
    """
    Department Update and Retrieve View for managing department-related operations.

    This view allows administrators to retrieve and update details of existing departments.
    It uses the `DepartmentSerializer` for data validation and serialization.
    """

    permission_classes = [IsAdminUser]
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()
