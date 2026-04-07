from django.urls import path
from .views import (
    PatientDashboardView,
    DoctorDashboardView,
    PharmacistDashboardView,
    CaretakerDashboardView,
    AdminDashboardView,
)

urlpatterns = [
    path('patient/',    PatientDashboardView.as_view(),    name='patient-dashboard'),
    path('doctor/',     DoctorDashboardView.as_view(),     name='doctor-dashboard'),
    path('pharmacist/', PharmacistDashboardView.as_view(), name='pharmacist-dashboard'),
    path('caretaker/',  CaretakerDashboardView.as_view(),  name='caretaker-dashboard'),
    path('admin/',      AdminDashboardView.as_view(),      name='admin-dashboard'),
]
