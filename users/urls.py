from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    RegisterPatientView,
    RegisterDoctorView,
    RegisterPharmacistView,
    RegisterCaretakerView,
    UserProfileView,
    ChangePasswordView,
)

urlpatterns = [
    # ── Tokens JWT ──────────────────────────────────────────────────────────
    path('token/',         CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(),          name='token_refresh'),

    # ── Inscription ─────────────────────────────────────────────────────────
    path('register/patient/',    RegisterPatientView.as_view(),    name='register_patient'),
    path('register/doctor/',     RegisterDoctorView.as_view(),     name='register_doctor'),
    path('register/pharmacist/', RegisterPharmacistView.as_view(), name='register_pharmacist'),  # BUG-18
    path('register/caretaker/',  RegisterCaretakerView.as_view(),  name='register_caretaker'),   # BUG-18

    # ── Profil & mot de passe ────────────────────────────────────────────────
    path('me/',               UserProfileView.as_view(),    name='user_profile'),
    path('password/change/',  ChangePasswordView.as_view(), name='password_change'),  # BUG-01
]
