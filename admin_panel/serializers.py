from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import AuditLog

# Import des modèles pour les profils détaillés
from patients.models import Patient, MedicalProfile, Antecedent
from doctors.models import Doctor, WeeklySchedule, DoctorQualification
from appointments.models import Appointment

User = get_user_model()

# ─── Profils Détaillés pour l'Admin ───────────────────────────────────────────

class AdminAntecedentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Antecedent
        fields = ['id', 'name', 'type', 'description', 'date_diagnosis']

class AdminMedicalProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalProfile
        fields = ['weight', 'height', 'allergies', 'chronic_diseases', 'current_medications']

class AdminPatientProfileSerializer(serializers.ModelSerializer):
    medical_profile = AdminMedicalProfileSerializer(read_only=True)
    antecedents = AdminAntecedentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Patient
        fields = ['medical_history', 'blood_group', 'medical_profile', 'antecedents']

class AdminScheduleSerializer(serializers.ModelSerializer):
    day_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    class Meta:
        model = WeeklySchedule
        fields = ['id', 'day_of_week', 'day_display', 'start_time', 'end_time', 'slot_duration', 'is_active']

class AdminDoctorProfileSerializer(serializers.ModelSerializer):
    schedules = AdminScheduleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Doctor
        fields = [
            'specialty', 'license_number', 'clinic_name', 'experience_years', 
            'bio', 'consultation_fee', 'rating', 'total_reviews', 'schedules'
        ]

class AdminUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    submitted_documents = serializers.SerializerMethodField()
    
    # Données étendues selon le rôle
    doctor_detail = AdminDoctorProfileSerializer(source='doctor_profile', read_only=True)
    patient_detail = AdminPatientProfileSerializer(source='patient_profile', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'full_name', 'first_name', 'last_name', 'email', 'role', 
            'is_active', 'verification_status', 'date_joined', 'phone',
            'city', 'wilaya', 'address', 'submitted_documents',
            'doctor_detail', 'patient_detail'
        ]

    def get_submitted_documents(self, obj):
        """Récupère dynamiquement les documents selon l'architecture exacte de la BDD"""
        docs = []
        request = self.context.get('request')
        
        # Fonction utilitaire pour générer l'URL absolue du fichier (ex: http://127.0.0.1:8000/media/...)
        def build_url(file_field):
            if file_field and hasattr(file_field, 'url'):
                return request.build_absolute_uri(file_field.url) if request else file_field.url
            return None

        try:
            if obj.role == 'doctor':
                # On utilise 'doctor_profile' comme défini dans ton modèle Doctor
                profile = getattr(obj, 'doctor_profile', None) 
                if profile:
                    # L'autorisation d'exercer
                    if getattr(profile, 'practice_authorization', None):
                        docs.append({
                            "title": "Autorisation d'exercer", 
                            "url": build_url(profile.practice_authorization)
                        })
                    
                    # Les diplômes liés via 'qualifications' (DoctorQualification)
                    for qual in profile.qualifications.all():
                        if getattr(qual, 'scan', None):
                            docs.append({
                                "title": f"Diplôme: {qual.title} ({qual.degree_type})", 
                                "url": build_url(qual.scan)
                            })

            elif obj.role == 'pharmacist':
                # On utilise 'pharmacist_profile'
                profile = getattr(obj, 'pharmacist_profile', None)
                if profile:
                    # La licence d'exploitation
                    if getattr(profile, 'pharmacy_license', None):
                        docs.append({
                            "title": "Licence d'exploitation", 
                            "url": build_url(profile.pharmacy_license)
                        })
                    
                    # Les diplômes (PharmacistQualification)
                    for qual in profile.qualifications.all():
                        if getattr(qual, 'scan', None):
                            docs.append({
                                "title": f"Diplôme: {qual.title}", 
                                "url": build_url(qual.scan)
                            })

            elif obj.role == 'caretaker':
                # On utilise 'caretaker_profile'
                profile = getattr(obj, 'caretaker_profile', None)
                if profile:
                    # Les certificats (CaretakerCertificate)
                    for cert in profile.certificates.all():
                        if getattr(cert, 'scan', None):
                            docs.append({
                                "title": f"Certificat: {cert.name}", 
                                "url": build_url(cert.scan)
                            })
                        
        except Exception as e:
            # Sécurité pour éviter un crash d'API si un profil est mal configuré
            print(f"Avertissement lors de la récupération des docs pour {obj.email}: {str(e)}")
            
        return docs

class AuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.get_full_name', read_only=True, default='Système')
    
    class Meta:
        model = AuditLog
        fields = ['id', 'level', 'message', 'actor_name', 'ip_address', 'created_at']