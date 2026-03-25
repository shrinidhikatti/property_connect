import django_filters
from .models import Property


class PropertyFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    min_area = django_filters.NumberFilter(field_name='area_sqft', lookup_expr='gte')
    max_area = django_filters.NumberFilter(field_name='area_sqft', lookup_expr='lte')
    bedrooms = django_filters.NumberFilter(field_name='bedrooms')
    min_bedrooms = django_filters.NumberFilter(field_name='bedrooms', lookup_expr='gte')

    class Meta:
        model = Property
        fields = ['property_type', 'city', 'locality', 'status', 'price_negotiable']
