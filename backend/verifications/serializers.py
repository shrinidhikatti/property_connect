from rest_framework import serializers
from .models import Verification
from properties.serializers import PropertyListSerializer
from documents.serializers import DocumentSerializer


class VerificationSerializer(serializers.ModelSerializer):
    property_detail = PropertyListSerializer(source='property', read_only=True)
    advocate_name = serializers.SerializerMethodField()
    documents = DocumentSerializer(source='property.documents', many=True, read_only=True)

    class Meta:
        model = Verification
        fields = (
            'id', 'property', 'property_detail', 'advocate_name', 'status',
            'remarks', 'rejection_reason', 'document_feedback',
            'documents', 'assigned_at', 'reviewed_at',
        )
        read_only_fields = ('id', 'assigned_at', 'reviewed_at', 'advocate_name')

    def get_advocate_name(self, obj):
        if obj.advocate:
            return obj.advocate.get_full_name() or obj.advocate.email
        return None


class VerificationActionSerializer(serializers.Serializer):
    """Used for approve / reject / request_changes actions."""
    remarks = serializers.CharField(required=False, allow_blank=True)
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
    document_feedback = serializers.DictField(required=False, default=dict)
