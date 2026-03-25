from django.urls import path, include
from rest_framework_nested import routers
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet

# Nested: /api/v1/properties/{property_pk}/documents/
# We wire this via properties/urls.py using a nested router
urlpatterns = []
