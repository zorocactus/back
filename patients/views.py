from rest_framework import generics, permissions
from .models import Patient, MedicalProfile, Antecedent, Treatment, LabResult, SymptomAnalysis
from .serializers import (
    PatientSerializer,
    MedicalProfileSerializer,
    AntecedentSerializer,
    TreatmentSerializer,
    LabResultSerializer,
    SymptomAnalysisSerializer
)
from appointments.permissions import IsPatient

class PatientProfileView(generics.RetrieveUpdateAPIView):
    """GET / PUT /api/patients/profile/ — own patient profile."""
    serializer_class = PatientSerializer
    permission_classes = [IsPatient]

    def get_object(self):
        return self.request.user.patient_profile

class MedicalProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = MedicalProfileSerializer
    permission_classes = [IsPatient]

    def get_object(self):
        return MedicalProfile.objects.get_or_create(patient=self.request.user.patient_profile)[0]

class AntecedentListView(generics.ListCreateAPIView):
    serializer_class = AntecedentSerializer
    permission_classes = [IsPatient]

    def get_queryset(self):
        return Antecedent.objects.filter(patient=self.request.user.patient_profile).order_by('-date_diagnosis', '-id')

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user.patient_profile)

class TreatmentListView(generics.ListCreateAPIView):
    serializer_class = TreatmentSerializer
    permission_classes = [IsPatient]

    def get_queryset(self):
        return Treatment.objects.filter(patient=self.request.user.patient_profile).order_by('-start_date', '-id')

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user.patient_profile)

class LabResultListView(generics.ListCreateAPIView):
    serializer_class = LabResultSerializer
    permission_classes = [IsPatient]

    def get_queryset(self):
        return LabResult.objects.filter(patient=self.request.user.patient_profile).order_by('-date', '-id')

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user.patient_profile)

class SymptomAnalysisListView(generics.ListCreateAPIView):
    serializer_class = SymptomAnalysisSerializer
    permission_classes = [IsPatient]

    def get_queryset(self):
        return SymptomAnalysis.objects.filter(patient=self.request.user.patient_profile).order_by('-date')

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user.patient_profile)

class DoctorPatientsListView(generics.ListAPIView):
    """GET /api/patients/my-patients/ — Liste des patients ayant un RDV avec le médecin."""
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        from rest_framework.exceptions import PermissionDenied
        if getattr(user, 'role', None) != 'doctor':
            raise PermissionDenied("Accès réservé aux médecins.")
        return Patient.objects.filter(appointments__doctor__user=user).distinct().order_by('user__last_name', 'user__first_name')


class PatientRecordView(generics.RetrieveAPIView):
    """
    GET /api/doctor/patients/{id}/record/
    BUG-05 fix : dossier médical complet d'un patient, accessible au médecin qui le suit.
    Retourne : profile, medical_profile, antecedents, treatments, lab_results
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        from rest_framework.exceptions import PermissionDenied
        from rest_framework.response import Response
        from appointments.models import Appointment

        if getattr(request.user, 'role', None) != 'doctor':
            raise PermissionDenied("Accès réservé aux médecins.")

        try:
            patient = Patient.objects.get(pk=pk)
        except Patient.DoesNotExist:
            from rest_framework import status as drf_status
            return Response({"detail": "Patient introuvable."}, status=drf_status.HTTP_404_NOT_FOUND)

        # Sécurité : le médecin ne peut voir que ses propres patients
        if not Appointment.objects.filter(doctor=request.user.doctor_profile, patient=patient).exists():
            raise PermissionDenied("Accès limité à vos propres patients.")

        try:
            medical = MedicalProfile.objects.get(patient=patient)
            medical_data = MedicalProfileSerializer(medical).data
        except MedicalProfile.DoesNotExist:
            medical_data = {}

        return Response({
            'profile':         PatientSerializer(patient).data,
            'medical_profile': medical_data,
            'antecedents':     AntecedentSerializer(Antecedent.objects.filter(patient=patient), many=True).data,
            'treatments':      TreatmentSerializer(Treatment.objects.filter(patient=patient), many=True).data,
            'lab_results':     LabResultSerializer(LabResult.objects.filter(patient=patient), many=True).data,
        })
