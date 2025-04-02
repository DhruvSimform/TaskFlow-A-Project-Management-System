# from django.shortcuts import render
# from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.


class Home(APIView):

    def get(self, request, *args, **kwargs):
        user = request.user  # Get the authenticated user
        return Response(
            data={
                "message": "Hello!",
                "user_info": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "name": user.name,
                },
            }
        )
