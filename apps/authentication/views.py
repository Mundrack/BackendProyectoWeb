from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    ChangePasswordSerializer
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Registro de nuevos usuarios"""
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    """Login de usuarios"""
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(email=email, password=password)

        if not user:
            return Response(
                {
                    'error': 'Credenciales inválidas',
                    'details': {
                        'non_field_errors': ['Email o contraseña incorrectos']
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {
                    'error': 'Cuenta desactivada',
                    'details': {
                        'non_field_errors': ['Esta cuenta ha sido desactivada']
                    }
                },
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        })


class ProfileView(generics.RetrieveUpdateAPIView):
    """Ver y actualizar perfil de usuario"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """Cambiar contraseña del usuario"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        # Verificar contraseña actual
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {
                    'error': 'Contraseña actual incorrecta',
                    'details': {
                        'old_password': ['La contraseña actual no es correcta']
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Establecer nueva contraseña
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({
            'message': 'Contraseña actualizada exitosamente'
        }, status=status.HTTP_200_OK)


class EmployeeListView(APIView):
    """Lista de empleados filtrada por compañía"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        company_id = request.query_params.get('company')

        # Filtrar empleados tipo 'employee'
        employees = User.objects.filter(user_type='employee', is_active=True)

        # Si el usuario es owner, filtrar por sus compañías
        if user.user_type == 'owner':
            from apps.companies.models import Company
            companies = Company.objects.filter(owner=user)
            if company_id:
                companies = companies.filter(id=company_id)
            # No aplicamos filtro de compañía aquí, devolvemos todos los employees
            # El owner puede asignar cualquier employee a sus equipos

        serializer = UserSerializer(employees, many=True)
        return Response(serializer.data)
