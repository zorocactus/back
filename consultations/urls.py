from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConsultationViewSet, CompleteSessionView, AddPrescriptionItemView

router = DefaultRouter()
router.register('consultations', ConsultationViewSet, basename='consultation')

urlpatterns = [
    # ── Routes custom AVANT le router pour éviter les conflits ────────────────
    # BUG-07 fix : POST /api/consultations/complete-session/
    path('consultations/complete-session/', CompleteSessionView.as_view(),    name='consultation-complete-session'),
    # BUG-06 fix : POST /api/consultations/prescriptions/
    path('consultations/prescriptions/',    AddPrescriptionItemView.as_view(), name='consultation-add-prescription'),

    # ── CRUD standard ─────────────────────────────────────────────────────────
    path('', include(router.urls)),
]
