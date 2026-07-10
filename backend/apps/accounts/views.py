from rest_framework import generics, permissions

from .serializers import ProfileSerializer, RegisterSerializer
from rest_framework.permissions import IsAuthenticated


class ProfileAPIView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
