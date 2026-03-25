from django.contrib import admin
from .models import Verification


@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ['property', 'advocate', 'status', 'assigned_at', 'reviewed_at']
    list_filter = ['status']
    search_fields = ['property__title', 'advocate__email']
    ordering = ['-assigned_at']
    readonly_fields = ['assigned_at', 'reviewed_at']
