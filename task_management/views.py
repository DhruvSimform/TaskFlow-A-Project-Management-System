from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Task
from .serializer import TaskSerializer

# Create your views here.


class Home(APIView):

    def get(self, *args, **kwargs):
        return Response({"Message": "Hello Task Management APP URL is working"})


class TaskListCreateView(ListCreateAPIView):
    serializer_class = TaskSerializer
    queryset = Task.objects.filter(parent_task=None)

    def perform_create(self, serializer):

        return serializer.save()


class TaskUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
