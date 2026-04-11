from datetime import timedelta

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from appointments.models import Appointment
from appointments.permissions import IsDoctor
from prescriptions.models import Prescription, PrescriptionItem, QRToken

from .models import Consultation
from .serializers import ConsultationSerializer


class ConsultationViewSet(viewsets.ModelViewSet):
    """CRUD standard des consultations."""
    queryset = Consultation.objects.select_related('doctor__user', 'patient__user', 'appointment').all()
    serializer_class = ConsultationSerializer
    permission_classes = [IsDoctor]

    def perform_create(self, serializer):
        consultation = serializer.save()
        if consultation.appointment:
            consultation.appointment.status = 'completed'
            consultation.appointment.save()

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, 'role', None)

        # IMP-08 : Réutilisation du select_related défini ligne 18
        qs = Consultation.objects.select_related('doctor__user', 'patient__user', 'appointment')

        if role == 'patient':
            return qs.filter(patient__user=user)
        if role == 'doctor':
            return qs.filter(doctor__user=user)
        if user.is_staff:
            return qs.all()
        return Consultation.objects.none()


# ── BUG-07 fix ────────────────────────────────────────────────────────────────

class CompleteSessionView(APIView):
    """
    POST /api/consultations/complete-session/
    BUG-07 fix : finalise une session de consultation.
    - Met à jour la Consultation (symptômes, diagnostic, statut=completed)
    - Marque le Appointment comme completed
    - Génère un QR token si une ordonnance existe
    Body : { appointment_id, symptoms, diagnosis }
    """
    permission_classes = [IsDoctor]

    def post(self, request):
        appointment_id = request.data.get('appointment_id')
        symptoms  = request.data.get('symptoms', '')
        diagnosis = request.data.get('diagnosis', '')

        # IMP-17 : Validation de l'ID obligatoire
        if not appointment_id:
            return Response({"detail": "appointment_id est requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            appt = Appointment.objects.get(pk=appointment_id, doctor=request.user.doctor_profile)
        except (Appointment.DoesNotExist, ValueError, TypeError):
            return Response({"detail": "Rendez-vous introuvable ou ID invalide."}, status=status.HTTP_404_NOT_FOUND)

        # Récupère ou crée la consultation liée
        consultation, _ = Consultation.objects.get_or_create(
            appointment=appt,
            defaults={
                'doctor':          appt.doctor,
                'patient':         appt.patient,
                'chief_complaint': symptoms or appt.motif,
                'consulted_at':    timezone.now(),
            },
        )

        # Met à jour les champs médicaux
        consultation.chief_complaint = symptoms or consultation.chief_complaint
        consultation.diagnosis       = diagnosis
        consultation.status          = Consultation.Status.COMPLETED
        consultation.save()

        # Marque le RDV comme terminé
        appt.status = 'completed'
        appt.save()

        # Notification patient
        from notifications.models import Notification
        Notification.objects.get_or_create(
            user=appt.patient.user,
            title="Consultation terminée",
            message="Votre consultation est terminée. Ordonnance disponible si prescrite.",
            notification_type='APPOINTMENT',
        )

        # Cherche si une ordonnance a été créée pendant la session
        prescription = consultation.prescriptions.first()
        prescription_token = None
        prescription_qr_url = None
        if prescription:
            qr, _ = QRToken.objects.get_or_create(prescription=prescription)
            prescription_token  = qr.token
            prescription_qr_url = f'/api/prescriptions/{prescription.id}/qr-image/'

        return Response({
            'consultation_id':    str(consultation.id),
            'prescription_token': prescription_token,
            'prescription_qr_url': prescription_qr_url,
        }, status=status.HTTP_200_OK)


# ── BUG-06 fix ────────────────────────────────────────────────────────────────

class AddPrescriptionItemView(APIView):
    """
    POST /api/consultations/prescriptions/
    BUG-06 fix : ajoute un médicament à l'ordonnance en cours.
    Crée la Consultation (brouillon) et la Prescription si elles n'existent pas encore.
    Body : { appointment_id, drug_name | medication, dosage, frequency, duration,
             instructions, quantity }
    """
    permission_classes = [IsDoctor]

    def post(self, request):
        appointment_id = request.data.get('appointment_id')

        # IMP-17 : Validation de l'ID obligatoire
        if not appointment_id:
            return Response({"detail": "appointment_id est requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            appt = Appointment.objects.get(pk=appointment_id, doctor=request.user.doctor_profile)
        except (Appointment.DoesNotExist, ValueError, TypeError):
            return Response({"detail": "Rendez-vous introuvable ou ID invalide."}, status=status.HTTP_404_NOT_FOUND)

        # Récupère ou crée la consultation brouillon
        consultation, _ = Consultation.objects.get_or_create(
            appointment=appt,
            defaults={
                'doctor':          appt.doctor,
                'patient':         appt.patient,
                'chief_complaint': appt.motif,
                'consulted_at':    timezone.now(),
                'status':          Consultation.Status.IN_PROGRESS,
            },
        )

        # Récupère ou crée une ordonnance brouillon
        prescription, _ = Prescription.objects.get_or_create(
            consultation=consultation,
            defaults={
                'valid_until': (timezone.now() + timedelta(days=30)).date(),
            },
        )

        # Résolution du nom du médicament
        medication_id = None
        raw_med = request.data.get('medication')
        drug_name = request.data.get('drug_name', '')

        if isinstance(raw_med, int) or (isinstance(raw_med, str) and raw_med.isdigit()):
            medication_id = int(raw_med)
        elif isinstance(raw_med, str) and raw_med:
            drug_name = drug_name or raw_med

        if not drug_name and medication_id:
            from medications.models import Medication as MedModel
            try:
                drug_name = MedModel.objects.get(pk=medication_id).name
            except MedModel.DoesNotExist:
                pass

        item = PrescriptionItem.objects.create(
            prescription  = prescription,
            medication_id = medication_id,
            drug_name     = drug_name or 'Médicament',
            dosage        = request.data.get('dosage', ''),
            frequency     = request.data.get('frequency', '1x_day'),
            duration      = request.data.get('duration', ''),
            instructions  = request.data.get('instructions', ''),
            quantity      = int(request.data.get('quantity', 1)),
        )

        return Response({
            'id':              item.id,
            'drug_name':       item.drug_name,
            'dosage':          item.dosage,
            'frequency':       item.frequency,
            'duration':        item.duration,
            'prescription_id': str(prescription.id),
        }, status=status.HTTP_201_CREATED)
