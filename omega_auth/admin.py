from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
import uuid
from .models import CustomUser, WaitingList


class CustomUserAdmin(UserAdmin):
    """Admin interface for the custom user model."""
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'email_verified', 'is_approved', 'is_staff', 'is_active')
    list_filter = ('email_verified', 'is_approved', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Status'), {'fields': ('email_verified', 'is_approved')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    readonly_fields = ('date_joined', 'last_login')
    
    actions = ['approve_users']
    
    def approve_users(self, request, queryset):
        """Approve selected users to use the platform."""
        updated = queryset.update(is_approved=True)
        
        # Send approval emails
        for user in queryset:
            # Generate login URL with frontend URL
            frontend_url = settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else 'http://localhost:3000'
            login_url = f"{frontend_url}/login"
            
            # Render HTML email
            html_message = render_to_string('auth/emails/account_approved.html', {
                'name': user.first_name,
                'login_url': login_url
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                'Your Account Has Been Approved',
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
        
        self.message_user(request, _(f"{updated} users were successfully approved."))
    
    approve_users.short_description = _("Approve selected users")


class WaitingListAdmin(admin.ModelAdmin):
    """Admin interface for the waiting list."""
    list_display = ('email', 'name', 'date_joined', 'is_invited', 'invitation_sent_at', 'display_invitation_token')
    list_filter = ('is_invited', 'date_joined')
    search_fields = ('email', 'name')
    readonly_fields = ('date_joined', 'display_full_token')
    fieldsets = (
        (None, {'fields': ('email', 'name', 'reason')}),
        (_('Status'), {'fields': ('is_invited', 'invitation_sent_at')}),
        (_('Invitation'), {'fields': ('display_full_token',)}),
        (_('Dates'), {'fields': ('date_joined',)}),
    )
    
    actions = ['send_invitations', 'regenerate_tokens']
    
    def display_invitation_token(self, obj):
        """Display a truncated version of the invitation token in the list view."""
        if obj.invitation_token:
            token_str = str(obj.invitation_token)
            return f"{token_str[:8]}...{token_str[-8:]}"
        return "-"
    display_invitation_token.short_description = _("Invitation Token")
    
    def display_full_token(self, obj):
        """Display the full invitation token with a copy button."""
        if obj.invitation_token:
            token_str = str(obj.invitation_token)
            return mark_safe(f"""
                <div style="display: flex; align-items: center;">
                    <code style="padding: 5px; background: #f5f5f5; border-radius: 3px;">{token_str}</code>
                    <button type="button" onclick="navigator.clipboard.writeText('{token_str}')" 
                            style="margin-left: 10px; padding: 3px 8px; cursor: pointer;">
                        Copy
                    </button>
                </div>
            """)
        return "-"
    display_full_token.short_description = _("Invitation Token")
    
    def regenerate_tokens(self, request, queryset):
        """Regenerate invitation tokens for selected entries."""
        count = 0
        for entry in queryset:
            entry.invitation_token = uuid.uuid4()
            entry.save()
            count += 1
        
        self.message_user(request, _(f"Generated new invitation tokens for {count} entries."))
    regenerate_tokens.short_description = _("Regenerate invitation tokens")
    
    def send_invitations(self, request, queryset):
        """Send invitations to selected waiting list entries."""
        updated = 0
        
        # Send invitation emails
        for entry in queryset:
            # Generate a unique invitation token if not already present
            if not entry.invitation_token:
                entry.invitation_token = uuid.uuid4()
                
            # Mark as invited
            entry.is_invited = True
            entry.invitation_sent_at = timezone.now()
            entry.save()
            updated += 1
            
            # Generate registration URL with token
            token_str = str(entry.invitation_token)
            # Use the frontend URL, not the backend API URL
            frontend_url = settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else 'http://localhost:3000'
            registration_url = f"{frontend_url}/register?email={entry.email}&token={token_str}"
            
            # Render HTML email
            html_message = render_to_string('auth/emails/invitation.html', {
                'name': entry.name,
                'registration_url': registration_url,
                'invitation_token': token_str
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                'Invitation to Join Codercops',
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [entry.email],
                html_message=html_message,
                fail_silently=False,
            )
        
        self.message_user(request, _(f"Invitations sent to {updated} waiting list entries."))
    
    send_invitations.short_description = _("Send invitations to selected entries")


# Register models with custom admin classes
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(WaitingList, WaitingListAdmin) 