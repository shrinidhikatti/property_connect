from django.utils import timezone
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Verification
from .serializers import VerificationSerializer, VerificationActionSerializer
from users.permissions import IsAdvocate


class VerificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VerificationSerializer
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get_queryset(self):
        return Verification.objects.filter(
            advocate=self.request.user
        ).select_related('property', 'property__owner').prefetch_related('property__documents')

    @action(detail=False, methods=['get'])
    def queue(self, request):
        """Pending verifications assigned to this advocate."""
        pending = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        verification = self.get_object()
        if verification.status != 'pending':
            return Response(
                {'error': True, 'message': 'Only pending verifications can be approved.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        with transaction.atomic():
            verification.status = 'approved'
            verification.reviewed_at = timezone.now()
            verification.save()
            verification.property.approve()
            verification.property.save()
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        verification = self.get_object()
        serializer = VerificationActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            verification.status = 'rejected'
            verification.rejection_reason = serializer.validated_data.get('rejection_reason', '')
            verification.reviewed_at = timezone.now()
            verification.save()
            verification.property.reject(verification.rejection_reason)
            verification.property.save()
        return Response({'status': 'rejected'})

    @action(detail=True, methods=['post'])
    def request_changes(self, request, pk=None):
        verification = self.get_object()
        serializer = VerificationActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            verification.status = 'changes_requested'
            verification.remarks = serializer.validated_data.get('remarks', '')
            verification.document_feedback = serializer.validated_data.get('document_feedback', {})
            verification.save()
            verification.property.request_changes(verification.remarks)
            verification.property.save()
        return Response({'status': 'changes_requested'})
