from rest_framework import serializers
from .models import Property, PropertyImage, Favorite


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ('id', 'image_url', 'thumbnail_url', 'order')


class PropertyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    cover_image = serializers.SerializerMethodField()
    owner_name = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    document_count = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = (
            'id', 'title', 'property_type', 'price', 'price_negotiable',
            'area_sqft', 'bedrooms', 'bathrooms', 'locality', 'city',
            'status', 'cover_image', 'owner_name', 'is_favorited',
            'document_count', 'created_at',
        )

    def get_cover_image(self, obj):
        img = obj.images.first()
        return img.thumbnail_url or img.image_url if img else None

    def get_owner_name(self, obj):
        return obj.owner.get_full_name() or obj.owner.username

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False

    def get_document_count(self, obj):
        return obj.documents.count()


class PropertyDetailSerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    owner_name = serializers.SerializerMethodField()
    owner_phone = serializers.SerializerMethodField()
    document_count = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = (
            'id', 'title', 'description', 'property_type', 'price', 'price_negotiable',
            'area_sqft', 'bedrooms', 'bathrooms', 'lat', 'lng', 'address', 'locality',
            'city', 'pincode', 'amenities', 'status', 'images', 'owner_name',
            'owner_phone', 'document_count', 'is_favorited', 'created_at', 'approved_at',
        )

    def get_owner_name(self, obj):
        return obj.owner.get_full_name() or obj.owner.username

    def get_owner_phone(self, obj):
        # Only reveal phone if buyer has an active conversation with contact_shared=True
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        from conversations.models import Conversation
        has_shared = Conversation.objects.filter(
            property=obj, buyer=request.user, contact_shared=True
        ).exists()
        return obj.owner.phone if has_shared else None

    def get_document_count(self, obj):
        return obj.documents.count()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False


class PropertyCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = (
            'title', 'description', 'property_type', 'price', 'price_negotiable',
            'area_sqft', 'bedrooms', 'bathrooms', 'lat', 'lng', 'address',
            'locality', 'city', 'pincode', 'amenities',
        )

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Price must be positive.')
        return value

    def validate_area_sqft(self, value):
        if value <= 0:
            raise serializers.ValidationError('Area must be positive.')
        return value
