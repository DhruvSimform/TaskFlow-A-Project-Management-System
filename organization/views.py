from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView

# Create your views here.
from account.models import CustomUser

from .permitions import IsAdminUser
from .serializers import DepartmentSerializer, UserRegistrationSerializer
from .services import create_department


class UserView(CreateAPIView, ListAPIView):
    lookup_field = "email"
    queryset = CustomUser.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = UserRegistrationSerializer


class DepartmentView(CreateAPIView, RetrieveUpdateAPIView, ListAPIView):
    # permission_classes = [IsAdminUser]
    serializer_class = DepartmentSerializer

    def perform_create(self, serializer):
        create_department(serializer.validated_data, self.request.user)
