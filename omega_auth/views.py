from django.shortcuts import get_object_or_404, render
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework import status, viewsets, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
import uuid

from .models import WaitingList
from .serializers import (
    WaitingListSerializer,
    UserRegistrationSerializer,
    LoginSerializer,
    UserSerializer,
    VerifyEmailSerializer
)

User = get_user_model()

class WaitingListViewSet(viewsets.ModelViewSet):
    """
    API endpoint to join the waiting list.
    """
    queryset = WaitingList.objects.all()
    serializer_class = WaitingListSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['post']  # Only allow POST requests
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        # Send confirmation email
        email = serializer.validated_data['email']
        name = serializer.validated_data['name']
        
        # Render HTML email
        html_message = render_to_string('auth/emails/waitlist_confirmation.html', {
            'name': name,
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            'Thank You for Joining Our Waiting List',
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration using invitation.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Get validated data
            email = serializer.validated_data['email']
            invitation_token = serializer.validated_data['invitation_token']
            
            try:
                # Check if email exists in waiting list, is invited, and the token matches
                waiting_list_entry = get_object_or_404(
                    WaitingList, 
                    email=email,
                    is_invited=True
                    )
                    
                # Validate invitation token
                if not waiting_list_entry.invitation_token or str(waiting_list_entry.invitation_token) != invitation_token:
                        return Response(
                            {"error": "Invalid invitation token for this email address."},
                            status=status.HTTP_400_BAD_REQUEST
                )
                
                # Create the user
                user = serializer.save()
                
                # Send verification email
                self.send_verification_email(user)
                
                return Response(
                    {"message": "User registered successfully. Please check your email to verify your account."},
                    status=status.HTTP_201_CREATED
                )
            except:
                return Resposnse(
                    {"error": "Invalid email or invitation token. You must be invited to register."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def send_verification_email(self, user):
        # Generate verification link with frontend URL
        frontend_url = settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else 'http://localhost:3000'
        verification_url = f"{frontend_url}/verify-email/{user.verification_token}"
        
        # Render HTML email
        html_message = render_to_string('auth/emails/verify_email.html', {
            'name': user.first_name,
            'verification_url': verification_url
        })
        plain_message = strip_tags(html_message)
        
        # Send verification email
        send_mail(
            'Verify Your Email Address',
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )


class LoginView(APIView):
    """
    API endpoint for user login.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            user = authenticate(email=email, password=password)
            
            if not user:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """
    API endpoint for user profile.
    """
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class VerifyEmailView(APIView):
    """
    API endpoint for email verification.
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, token=None):
        """Handle GET requests for email verification links."""
        if not token:
            # If token is not in the URL, check if it's in the query params
            token = request.query_params.get('token')
            
        if not token:
            # Render error page
            frontend_url = settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else 'http://localhost:3000'
            return render(
                request, 
                'auth/email_verification.html', 
                {
                    'success': False,
                    'error_message': 'Invalid verification token.',
                    'contact_url': f"{frontend_url}/contact"
                }
            )
            
        try:
            user = User.objects.get(verification_token=uuid.UUID(token))
            
            if user.email_verified:
                # Already verified
                frontend_url = settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else 'http://localhost:3000'
                return render(
                    request, 
                    'auth/email_verification.html',
                    {
                        'success': True,
                        'login_url': f"{frontend_url}/login"
                    }
                )
            
            # Mark email as verified
            user.email_verified = True
            user.save()
            
            # Render success page
            frontend_url = settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else 'http://localhost:3000'
            return render(
                request, 
                'auth/email_verification.html',
                {
                    'success': True,
                    'login_url': f"{frontend_url}/login"
                }
            )
            
        except (User.DoesNotExist, ValueError):
            # Render error page for invalid token
            frontend_url = settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else 'http://localhost:3000'
            return render(
                request, 
                'auth/email_verification.html', 
                {
                    'success': False,
                    'error_message': 'Invalid verification token or expired link.',
                    'contact_url': f"{frontend_url}/contact"
                }
            )
    
    def post(self, request):
        """Handle POST requests for programmatic verification (API use)."""
        serializer = VerifyEmailSerializer(data=request.data)
        
        if serializer.is_valid():
            token = serializer.validated_data['token']
            
            try:
                user = User.objects.get(verification_token=token)
                
                if user.email_verified:
                    return Response(
                        {"message": "Email already verified"},
                        status=status.HTTP_200_OK
                    )
                
                # Mark email as verified
                user.email_verified = True
                user.save()
                
                return Response(
                    {"message": "Email verified successfully"},
                    status=status.HTTP_200_OK
                )
            
            except User.DoesNotExist:
                return Response(
                    {"error": "Invalid verification token"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 