from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView

# Create your views here.
from account.models import CustomUser

from .models import Department
from .permitions import IsAdminUser
from .serializers import DepartmentSerializer, UserRegistrationSerializer
from .services import create_department


class UserView(CreateAPIView, ListAPIView):
    """
    API view for creating and listing users, restricted to admin users.
    """

    permission_classes = [IsAdminUser]
    lookup_field = "email"
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer


class UserUpdateRetriveView(RetrieveUpdateAPIView):
    """
    User Update and Retrieve View for administrators to manage user details using email lookup.
    """

    permission_classes = [IsAdminUser]
    lookup_field = "email"
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer


class DepartmentView(CreateAPIView, ListAPIView):
    """View for creating and listing departments using `DepartmentSerializer`."""

    permission_classes = [IsAdminUser]
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()

    def perform_create(self, serializer):
        create_department(serializer.validated_data, self.request.user)


class DepartmentUpdateRetriveView(RetrieveUpdateAPIView):
    """
    View for retrieving and updating department details, restricted to admin users.
    """

    permission_classes = [IsAdminUser]
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()
