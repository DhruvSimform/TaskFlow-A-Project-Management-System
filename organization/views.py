from rest_framework.generics import CreateAPIView

from .permitions import IsAdminUser
from .serializers import UserRegistrationSerializer

# Create your views here.


class CreateUserView(CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserRegistrationSerializer
