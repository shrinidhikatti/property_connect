import hashlib
import os
import re
import uuid

import boto3
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from properties.models import Property
from .models import Document
from .serializers import DocumentSerializer
from users.throttles import UploadRateThrottle

ALLOWED_MIME_TYPES = {'application/pdf', 'image/jpeg', 'image/png'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def _detect_mime(file):
    """Detect MIME type from file header bytes (no python-magic dependency in dev)."""
    header = file.read(8)
    file.seek(0)
    if header[:4] == b'%PDF':
        return 'application/pdf'
    if header[:3] == b'\xff\xd8\xff':
        return 'image/jpeg'
    if header[:8] == b'\x89PNG\r\n\x1a\n':
        return 'image/png'
    return 'application/octet-stream'


class DocumentViewSet(ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        prop = self._get_property()
        return Document.objects.filter(property=prop)

    def _get_property(self):
        return get_object_or_404(Property, pk=self.kwargs['property_pk'])

    def create(self, request, property_pk=None):
        prop = get_object_or_404(Property, pk=property_pk, owner=request.user)

        file = request.FILES.get('file')
        if not file:
            return Response({'error': True, 'message': 'No file provided.'}, status=400)
        doc_type = request.data.get('doc_type')
        if not doc_type:
            return Response({'error': True, 'message': 'doc_type is required.'}, status=400)

        if file.size > MAX_FILE_SIZE:
            return Response({'error': True, 'message': 'File too large. Max 10MB.'}, status=400)

        detected_mime = _detect_mime(file)
        if detected_mime not in ALLOWED_MIME_TYPES:
            return Response(
                {'error': True, 'message': 'Invalid file type. Only PDF, JPG, PNG allowed.'},
                status=400
            )

        safe_name = re.sub(r'[^\w.\-]', '_', os.path.basename(file.name))

        sha256 = hashlib.sha256()
        for chunk in file.chunks():
            sha256.update(chunk)
        checksum = sha256.hexdigest()
        file.seek(0)

        # Upload to S3 (skip if AWS keys not configured — dev mode)
        s3_key = f'documents/{prop.id}/{uuid.uuid4()}/{safe_name}'
        file_url = f'https://{settings.AWS_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}'

        if settings.AWS_ACCESS_KEY_ID:
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
            )
            s3.upload_fileobj(
                file, settings.AWS_BUCKET_NAME, s3_key,
                ExtraArgs={'ContentType': detected_mime, 'ServerSideEncryption': 'AES256'},
            )

        document = Document.objects.create(
            property=prop,
            doc_type=doc_type,
            s3_key=s3_key,
            file_url=file_url,
            file_name=safe_name,
            file_size=file.size,
            mime_type=detected_mime,
            checksum=checksum,
        )
        return Response(DocumentSerializer(document).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def download_url(self, request, property_pk=None, pk=None):
        document = get_object_or_404(Document, pk=pk, property__pk=property_pk)

        # Only owner or assigned advocate can download
        prop = document.property
        is_owner = prop.owner == request.user
        is_assigned_advocate = prop.verifications.filter(
            advocate=request.user, status='pending'
        ).exists()
        if not (is_owner or is_assigned_advocate or request.user.is_staff):
            return Response({'error': True, 'message': 'Permission denied.'}, status=403)

        if not settings.AWS_ACCESS_KEY_ID:
            return Response({'url': document.file_url})  # Dev fallback

        s3 = boto3.client('s3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.AWS_BUCKET_NAME, 'Key': document.s3_key},
            ExpiresIn=1800,
        )
        return Response({'url': url})
