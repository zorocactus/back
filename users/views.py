from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    CustomTokenObtainPairSerializer,
    RegisterPatientSerializer,
    RegisterDoctorSerializer,
    RegisterPharmacistSerializer,
    RegisterCaretakerSerializer,
    ChangePasswordSerializer,
    UserSerializer,
)
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ── Inscription ───────────────────────────────────────────────────────────────

class RegisterPatientView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterPatientSerializer
    permission_classes = [permissions.AllowAny]


class RegisterDoctorView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterDoctorSerializer
    permission_classes = [permissions.AllowAny]


class RegisterPharmacistView(generics.CreateAPIView):
    """BUG-18 fix : endpoint dédié pour l'inscription des pharmaciens."""
    queryset = User.objects.all()
    serializer_class = RegisterPharmacistSerializer
    permission_classes = [permissions.AllowAny]


class RegisterCaretakerView(generics.CreateAPIView):
    """BUG-18 fix : endpoint dédié pour l'inscription des gardes-malades."""
    queryset = User.objects.all()
    serializer_class = RegisterCaretakerSerializer
    permission_classes = [permissions.AllowAny]


# ── Profil ────────────────────────────────────────────────────────────────────

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/auth/me/ — profil de l'utilisateur connecté
    PUT   /api/auth/me/ — mise à jour complète
    PATCH /api/auth/me/ — mise à jour partielle (BUG-11 : déjà supporté par RetrieveUpdateAPIView)
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# ── Mot de passe ──────────────────────────────────────────────────────────────

class ChangePasswordView(APIView):
    """
    POST /api/auth/password/change/
    BUG-01 fix : endpoint manquant ajouté.
    Body : { old_password, new_password }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(
            {"detail": "Mot de passe modifié avec succès."},
            status=status.HTTP_200_OK,
        )
