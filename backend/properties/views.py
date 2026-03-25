import math
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django_fsm import TransitionNotAllowed

from .models import Property, PropertyImage, Favorite
from .serializers import (
    PropertyListSerializer, PropertyDetailSerializer,
    PropertyCreateUpdateSerializer, PropertyImageSerializer,
)
from .filters import PropertyFilter
from users.permissions import IsSeller, IsOwnerOrReadOnly
from verifications.services import assign_advocate_to_property


class PropertyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PropertyFilter
    search_fields = ['title', 'description', 'locality', 'address']
    ordering_fields = ['price', 'area_sqft', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Property.objects.select_related('owner').prefetch_related('images')

    def get_serializer_class(self):
        if self.action == 'list':
            return PropertyListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return PropertyCreateUpdateSerializer
        return PropertyDetailSerializer

    def get_permissions(self):
        if self.action in ('create',):
            return [IsAuthenticated(), IsSeller()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        # Public list shows only approved properties; owners see their own
        qs = self.get_queryset()
        if request.user.is_authenticated:
            qs = qs.filter(status='approved') | qs.filter(owner=request.user)
        else:
            qs = qs.filter(status='approved')
        qs = self.filter_queryset(qs.distinct())
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page or qs, many=True)
        return self.get_paginated_response(serializer.data) if page else Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # ─── Custom actions ───────────────────────────────────────────────────────

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_listings(self, request):
        qs = Property.objects.filter(owner=request.user).order_by('-created_at')
        serializer = PropertyListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def submit(self, request, pk=None):
        prop = get_object_or_404(Property, pk=pk, owner=request.user)
        try:
            with transaction.atomic():
                prop.submit_for_review()
                prop.save()
                assign_advocate_to_property(prop)
        except Exception as e:
            return Response({'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': prop.status})

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        prop = get_object_or_404(Property, pk=pk, status='approved')
        if request.method == 'POST':
            Favorite.objects.get_or_create(user=request.user, property=prop)
            return Response({'favorited': True})
        Favorite.objects.filter(user=request.user, property=prop).delete()
        return Response({'favorited': False})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def favorites(self, request):
        prop_ids = Favorite.objects.filter(user=request.user).values_list('property_id', flat=True)
        qs = Property.objects.filter(id__in=prop_ids, status='approved')
        serializer = PropertyListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Bounding-box proximity search (works without PostGIS)."""
        try:
            lat = float(request.query_params['lat'])
            lng = float(request.query_params['lng'])
            radius_km = float(request.query_params.get('radius', 5))
        except (KeyError, ValueError):
            return Response(
                {'error': True, 'message': 'lat and lng are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Approximate degree offsets for the radius
        lat_delta = radius_km / 111.0
        lng_delta = radius_km / (111.0 * math.cos(math.radians(lat)))

        qs = Property.objects.filter(
            status='approved',
            lat__range=(lat - lat_delta, lat + lat_delta),
            lng__range=(lng - lng_delta, lng + lng_delta),
        )
        serializer = PropertyListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)
