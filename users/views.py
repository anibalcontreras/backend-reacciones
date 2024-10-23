from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, UserSerializer
from .models import User

from rest_framework_simplejwt.authentication import JWTAuthentication



class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generar los tokens JWT
            refresh = user.get_token()  # Llama al método get_token del modelo User

             # Agregar print para verificar el token generado y el user_type
            print(f"Generando token para {user.username} con user_type: {user.user_type}")
            print(f"Access Token: {refresh.access_token}")
            print(f"Refresh Token: {refresh}")

            
            return Response({
                "message": "Login successful",
                "username": user.username,
                "user_type": user.user_type,
                "access": str(refresh.access_token),  # Token de acceso
                "refresh": str(refresh),  # Token de refresco
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()  # Selecciona todos los usuarios
    serializer_class = UserSerializer
    
class UserDetailView(APIView):
    """
    Vista para obtener la información personal del usuario autenticado.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]  # Solo usuarios autenticados

    def get(self, request, *args, **kwargs):
        try:
            user = request.user  # Obtener el usuario actual desde el token
            serializer = UserSerializer(user)  # Serializar el usuario
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

class RecipientListView(generics.ListAPIView):
    queryset = User.objects.filter(user_type='recipient')  # Aquí podrías agregar filtros si es necesario
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]  # Solo usuarios autenticados pueden hacer la solicitud

        
