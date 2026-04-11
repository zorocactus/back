import uuid
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from patients.models import Patient
from doctors.models import Doctor
from pharmacy.models import Pharmacist
from caretaker.models import Caretaker

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['full_name'] = user.get_full_name()
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role
        data['full_name'] = self.user.get_full_name()
        data['email'] = self.user.email
        return data


class RegisterUserSerializer(serializers.ModelSerializer):
    password         = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password_confirm', 'role', 'phone']

    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return data


# ── Patient ───────────────────────────────────────────────────────────────────

class RegisterPatientSerializer(RegisterUserSerializer):
    """
    Champs supplémentaires acceptés : sex, date_of_birth, address.
    BUG-12 fix : ces champs sont optionnels et mappés aux champs du modèle User.
    """
    sex           = serializers.CharField(required=False, allow_blank=True, default='')
    date_of_birth = serializers.DateField(required=False, allow_null=True, default=None)
    address       = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta(RegisterUserSerializer.Meta):
        fields = RegisterUserSerializer.Meta.fields + ['sex', 'date_of_birth', 'address']

    def create(self, validated_data):
        validated_data['role'] = 'patient'
        user = User.objects.create_user(**validated_data)
        Patient.objects.create(user=user)
        return user


# ── Médecin ───────────────────────────────────────────────────────────────────

class RegisterDoctorSerializer(RegisterUserSerializer):
    """
    BUG-13 fix : license_number et experience_years sont maintenant optionnels.
    Le champ sex est accepté (mappé vers user.sex).
    """
    specialty        = serializers.CharField(write_only=True, required=False, allow_blank=True, default='Généraliste')
    license_number   = serializers.CharField(write_only=True, required=False, allow_blank=True, default='')
    experience_years = serializers.IntegerField(write_only=True, required=False, default=0)
    sex              = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta(RegisterUserSerializer.Meta):
        fields = RegisterUserSerializer.Meta.fields + ['specialty', 'license_number', 'experience_years', 'sex']

    def create(self, validated_data):
        specialty        = validated_data.pop('specialty', 'Généraliste')
        license_number   = validated_data.pop('license_number', '')
        experience_years = validated_data.pop('experience_years', 0)
        validated_data['role'] = 'doctor'
        user = User.objects.create_user(**validated_data)
        Doctor.objects.create(
            user=user,
            specialty=specialty,
            license_number=license_number,
            experience_years=experience_years,
        )
        return user


# ── Pharmacien ────────────────────────────────────────────────────────────────

class RegisterPharmacistSerializer(RegisterUserSerializer):
    """
    BUG-18 fix : endpoint dédié pour les pharmaciens.
    Crée un profil Pharmacist minimal — à compléter dans les paramètres.
    """
    sex = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta(RegisterUserSerializer.Meta):
        fields = RegisterUserSerializer.Meta.fields + ['sex']

    def create(self, validated_data):
        validated_data['role'] = 'pharmacist'
        user = User.objects.create_user(**validated_data)
        Pharmacist.objects.create(
            user=user,
            license_number=f'PENDING-{uuid.uuid4().hex[:8].upper()}',
            pharmacy_name='À compléter',
            address='À compléter',
            city='',
        )
        return user


# ── Garde-malade ──────────────────────────────────────────────────────────────

class RegisterCaretakerSerializer(RegisterUserSerializer):
    """
    BUG-18 fix : endpoint dédié pour les gardes-malades.
    Crée un profil Caretaker minimal — à compléter dans les paramètres.
    """
    sex = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta(RegisterUserSerializer.Meta):
        fields = RegisterUserSerializer.Meta.fields + ['sex']

    def create(self, validated_data):
        validated_data['role'] = 'caretaker'
        user = User.objects.create_user(**validated_data)
        Caretaker.objects.create(user=user)
        return user


# ── Changement de mot de passe ────────────────────────────────────────────────

class ChangePasswordSerializer(serializers.Serializer):
    """BUG-01 fix : endpoint POST /api/auth/password/change/"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Mot de passe actuel incorrect.")
        return value


# ── Profil utilisateur ────────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'role', 'phone',
            'sex', 'date_of_birth', 'city', 'verification_status'
        ]
        read_only_fields = ['role', 'verification_status']
