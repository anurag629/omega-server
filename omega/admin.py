from django.contrib import admin
from .models import ManimScript


@admin.register(ManimScript)
class ManimScriptAdmin(admin.ModelAdmin):
    list_display = ('id', 'provider', 'status', 'created_at')
    list_filter = ('provider', 'status', 'created_at')
    search_fields = ('prompt', 'id')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('prompt', 'provider', 'status', 'created_at', 'updated_at')
        }),
        ('Script Details', {
            'fields': ('script', 'script_path')
        }),
        ('Output Details', {
            'fields': ('output_path', 'output_url')
        }),
        ('Error Details', {
            'fields': ('error_message',),
            'classes': ('collapse',),
        }),
    ) 