from rest_framework import permissions

class IsApprovedUser(permissions.BasePermission):
    """
    Custom permission to only allow approved users to access the view.
    """
    message = "Your account is not yet approved. Please wait for admin approval."
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_approved


class IsVerifiedUser(permissions.BasePermission):
    """
    Custom permission to only allow users with verified emails to access the view.
    """
    message = "Your email is not verified. Please check your email for the verification link."
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.email_verified


class IsApprovedAndVerifiedUser(permissions.BasePermission):
    """
    Custom permission to only allow approved and email-verified users to access the view.
    """
    message = "Your account must be verified and approved to access this resource."
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if not request.user.email_verified:
            self.message = "Your email is not verified. Please check your email for the verification link."
            return False
        
        if not request.user.is_approved:
            self.message = "Your account is not yet approved. Please wait for admin approval."
            return False
        
        return True 