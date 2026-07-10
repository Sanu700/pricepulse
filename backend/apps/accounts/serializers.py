from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
import re


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone_number",
            "city",
        )
        read_only_fields = ("id",)
    
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
        
    def validate_phone_number(self, value):


      if not re.fullmatch(r"[6-9]\d{9}", value):
        raise serializers.ValidationError(
            "Enter a valid Indian phone number."
        )

      return value

    def validate_email(self, value):

      if User.objects.filter(email=value).exists():
        raise serializers.ValidationError(
            "Email already exists."
        )

      return value

    def validate_username(self, value):

      if len(value) < 4:
        raise serializers.ValidationError(
            "Username must contain at least 4 characters."
        )

      return value
    
    def validate_password(self, value):

      if len(value) < 8:
        raise serializers.ValidationError(
            "Password should be at least 8 characters."
        )

      if not any(c.isupper() for c in value):
        raise serializers.ValidationError(
            "Password must contain an uppercase letter."
        )

      if not any(c.isdigit() for c in value):
        raise serializers.ValidationError(
            "Password must contain a number."
        )

      return value

