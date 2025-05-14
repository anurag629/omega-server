from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import WaitingList

User = get_user_model()


class WaitingListSerializer(serializers.ModelSerializer):
    """Serializer for the waiting list registration."""
    
    class Meta:
        model = WaitingList
        fields = ['email', 'name', 'reason']
        extra_kwargs = {'email': {'required': True}}


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration with invitation code."""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    invitation_token = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password2', 'invitation_token']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }

    def validate(self, attrs):
        # Validate password match
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Validate invitation token
        # The token validation will be handled in the view
        
        return attrs

    def create(self, validated_data):
        # Remove fields not part of the User model
        validated_data.pop('password2')
        validated_data.pop('invitation_token')
        
        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        user.set_password(validated_data['password'])
        user.save()
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data."""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'email_verified', 'is_approved', 'date_joined']
        read_only_fields = ['id', 'email', 'email_verified', 'is_approved', 'date_joined']


class VerifyEmailSerializer(serializers.Serializer):
    """Serializer for email verification."""
    token = serializers.UUIDField(required=True) 