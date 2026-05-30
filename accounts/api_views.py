from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


class OperatorMe(APIView):
    """Return basic info about the authenticated user for mobile clients using token auth."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = getattr(user, 'profile', None)
        role = 'admin' if user.is_superuser else (getattr(profile, 'role', '') if profile else '')
        return Response({
            'username': user.username,
            'email': user.email,
            'full_name': user.get_full_name(),
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'role': role,
        })
