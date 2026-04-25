# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'avatar']
        read_only_fields = ['id']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "رمزهای عبور مطابقت ندارند."})
        # بررسی یکتایی شماره تلفن (اختیاری)
        phone = attrs.get('phone_number')
        if phone and User.objects.filter(phone_number=phone).exists():
            raise serializers.ValidationError({"phone_number": "این شماره تلفن قبلاً ثبت شده است."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_new_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({"confirm_new_password": "رمزهای جدید مطابقت ندارند."})
        return attrs