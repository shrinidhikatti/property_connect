from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers
from .views import PropertyViewSet
from documents.views import DocumentViewSet

router = DefaultRouter()
router.register('', PropertyViewSet, basename='property')

# Nested: /api/v1/properties/{property_pk}/documents/
docs_router = nested_routers.NestedDefaultRouter(router, '', lookup='property')
docs_router.register('documents', DocumentViewSet, basename='property-documents')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(docs_router.urls)),
]
