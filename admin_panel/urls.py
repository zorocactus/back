from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminUserManagementViewSet, AuditLogViewSet, AdminAppointmentViewSet, AdminQueueViewSet

router = DefaultRouter()
router.register(r'users', AdminUserManagementViewSet, basename='admin-users')
router.register(r'audit-logs', AuditLogViewSet, basename='admin-audit-logs')
router.register(r'appointments', AdminAppointmentViewSet, basename='admin-appointments')
router.register(r'queue', AdminQueueViewSet, basename='admin-queue')

urlpatterns = [
    path('', include(router.urls)),
]