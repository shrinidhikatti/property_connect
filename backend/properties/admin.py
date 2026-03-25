from django.contrib import admin
from .models import Property, PropertyImage, Favorite


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 0
    readonly_fields = ['uploaded_at']


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'property_type', 'status', 'city', 'price', 'created_at']
    list_filter = ['status', 'property_type', 'city']
    search_fields = ['title', 'locality', 'owner__email']
    readonly_fields = ['created_at', 'updated_at', 'approved_at', 'expires_at']
    inlines = [PropertyImageInline]
    actions = ['soft_delete_selected']

    def soft_delete_selected(self, request, queryset):
        for obj in queryset:
            obj.delete()
    soft_delete_selected.short_description = 'Soft-delete selected properties'
