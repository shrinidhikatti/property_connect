# Belagavi Property Connect — Implementation Plan

> **P2P Real Estate Marketplace with Advocate Verification**  
> Target Launch: Belagavi, Karnataka  
> Stack: Django + React (Vite) + PostgreSQL/PostGIS  

---

## Overview

| Phase | Duration | Focus | Deliverable |
|-------|----------|-------|-------------|
| Phase 1 | 2 weeks | Foundation | Auth + basic CRUD |
| Phase 2 | 3 weeks | Core features | Listings + verification workflow |
| Phase 3 | 2 weeks | Communication | Chat + notifications |
| Phase 4 | 2 weeks | Payments + PWA | Monetization + offline |
| Phase 5 | 1 week | Launch prep | Deployment + QA |
| Phase 6 | Ongoing | Post-launch | Marketing + iteration |

**Total MVP Timeline: 10 weeks**

---

## Phase 1: Foundation (Week 1-2)

### Goals
- Project scaffolding with best practices
- User authentication with role-based access
- Basic API structure

### Backend Tasks

#### 1.1 Project Setup
```bash
# Create Django project
django-admin startproject config .
python manage.py startapp users
python manage.py startapp properties
python manage.py startapp documents
python manage.py startapp verifications
python manage.py startapp conversations
python manage.py startapp payments
python manage.py startapp cities
```

#### 1.2 Core Configuration
- [ ] `settings/base.py`, `settings/dev.py`, `settings/prod.py` split
- [ ] Environment variables via `python-decouple`
- [ ] PostgreSQL + PostGIS connection
- [ ] Redis connection for caching
- [ ] CORS configuration for frontend
- [ ] Logging setup (console + file)

#### 1.3 Custom User Model
```python
# users/models.py
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    phone = models.CharField(max_length=15, unique=True, null=True)
    role = models.CharField(max_length=20, choices=[
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('builder', 'Builder'),
        ('advocate', 'Advocate'),
    ], default='buyer')
    is_phone_verified = models.BooleanField(default=False)
    city = models.ForeignKey('cities.City', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### 1.4 Authentication Endpoints
- [ ] `POST /api/v1/auth/register/` — Email + phone + password
- [ ] `POST /api/v1/auth/login/` — Returns JWT tokens
- [ ] `POST /api/v1/auth/refresh/` — Refresh access token
- [ ] `POST /api/v1/auth/otp/send/` — Send OTP to phone
- [ ] `POST /api/v1/auth/otp/verify/` — Verify OTP
- [ ] `GET /api/v1/users/me/` — Current user profile
- [ ] `PATCH /api/v1/users/me/` — Update profile

#### 1.5 API Rate Limiting
```python
# config/settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/min',
        'user': '300/min',
        'auth': '5/min',      # Login / OTP send endpoints
        'uploads': '20/hour', # Document/image uploads
    }
}

# users/throttles.py
from rest_framework.throttling import AnonRateThrottle

class AuthRateThrottle(AnonRateThrottle):
    scope = 'auth'

class UploadRateThrottle(UserRateThrottle):
    scope = 'uploads'
```

Apply tighter throttles on sensitive endpoints:
```python
# users/views.py
class LoginView(TokenObtainPairView):
    throttle_classes = [AuthRateThrottle]  # 5/min per IP

class OTPSendView(APIView):
    throttle_classes = [AuthRateThrottle]
```

#### 1.6 Standardized Error Response Format
```python
# config/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            'error': True,
            'message': _flatten_errors(response.data),
            'code': response.status_code,
            'details': response.data if isinstance(response.data, dict) else {}
        }

    return response

def _flatten_errors(data):
    if isinstance(data, list):
        return data[0] if data else 'An error occurred'
    if isinstance(data, dict):
        for key, val in data.items():
            if key == 'detail':
                return str(val)
            return str(val[0]) if isinstance(val, list) else str(val)
    return str(data)

# config/settings/base.py
REST_FRAMEWORK = {
    ...
    'EXCEPTION_HANDLER': 'config.exceptions.custom_exception_handler',
}
```

#### 1.7 Permission Classes
```python
# users/permissions.py
class IsBuyer(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'buyer'

class IsSeller(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['seller', 'builder']

class IsAdvocate(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'advocate'

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user
```

### Frontend Tasks

#### 1.8 Vite + React Setup
```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install react-router-dom @tanstack/react-query zustand 
npm install axios react-hook-form zod @hookform/resolvers
npm install tailwindcss postcss autoprefixer
npm install react-helmet-async
```

#### 1.9 Project Structure
```
frontend/
├── src/
│   ├── api/              # Axios instance, API functions
│   │   ├── client.js     # Axios with interceptors
│   │   ├── auth.js       # Auth endpoints
│   │   └── properties.js # Property endpoints
│   ├── components/       # Reusable components
│   │   ├── ui/           # Button, Input, Card, Modal
│   │   ├── layout/       # Header, Footer, Sidebar
│   │   └── forms/        # LoginForm, RegisterForm
│   ├── features/         # Feature-specific components
│   │   ├── auth/
│   │   ├── properties/
│   │   └── chat/
│   ├── hooks/            # Custom hooks
│   │   ├── useAuth.js
│   │   └── useProperties.js
│   ├── pages/            # Route pages
│   ├── store/            # Zustand stores
│   ├── utils/            # Helpers, constants
│   └── App.jsx
├── public/
└── index.html
```

#### 1.10 Auth Flow Implementation
- [ ] Login page with phone/email + password
- [ ] Register page with role selection
- [ ] OTP verification screen
- [ ] JWT token storage (httpOnly cookie or secure localStorage)
- [ ] Axios interceptor for token refresh
- [ ] Protected route wrapper component
- [ ] Auth context/store with Zustand

#### 1.11 Base UI Components
- [ ] Button (primary, secondary, outline variants)
- [ ] Input (text, phone, password with validation)
- [ ] Card component
- [ ] Modal component
- [ ] Toast/notification system
- [ ] Loading spinner
- [ ] Empty state component

### Phase 1 Deliverables
- [x] User can register with email/phone
- [x] User can login and receive JWT
- [x] User can verify phone via OTP
- [x] Role-based access control working
- [x] Frontend auth flow complete
- [x] Basic responsive layout

---

## Phase 2: Core Property Features (Week 3-5)

### Goals
- Complete property CRUD
- Document upload and management
- Advocate verification workflow
- Geo search with PostGIS

### Backend Tasks

#### 2.1 Soft Delete Mixin (Shared)
```python
# core/models.py
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class SoftDeleteModel(models.Model):
    """Inherit from this instead of hard-deleting records."""
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Includes deleted records

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    class Meta:
        abstract = True
```

#### 2.2 Property Model
```python
# properties/models.py
from django.contrib.gis.db import models as gis_models
from django_fsm import FSMField, transition

class Property(SoftDeleteModel):  # Soft delete instead of hard delete
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    
    # Basic info
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    property_type = models.CharField(max_length=30, choices=[
        ('plot', 'Plot'),
        ('apartment', 'Apartment'),
        ('villa', 'Villa/House'),
        ('commercial', 'Commercial'),
        ('pg', 'PG/Hostel'),
    ])
    
    # Pricing
    price = models.DecimalField(max_digits=12, decimal_places=2)
    price_negotiable = models.BooleanField(default=True)
    
    # Size
    area_sqft = models.PositiveIntegerField()
    bedrooms = models.PositiveSmallIntegerField(null=True, blank=True)
    bathrooms = models.PositiveSmallIntegerField(null=True, blank=True)
    
    # Location (PostGIS)
    location = gis_models.PointField(srid=4326)
    address = models.TextField()
    locality = models.CharField(max_length=100)
    city = models.ForeignKey('cities.City', on_delete=models.PROTECT)
    pincode = models.CharField(max_length=6)
    
    # Amenities (JSONB)
    amenities = models.JSONField(default=list)
    
    # Status (FSM)
    status = FSMField(default='draft')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # Auto-expire after 90 days

    # Managers
    objects = PropertyManager()  # City-scoped, excludes soft-deleted
    all_objects = models.Manager()

    class Meta:
        indexes = [
            models.Index(fields=['status', 'city']),
            models.Index(fields=['property_type', 'city']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
            models.Index(fields=['expires_at']),
            gis_models.indexes.GistIndex(fields=['location']),  # PostGIS spatial index
        ]
    
    # FSM Transitions
    @transition(field=status, source='draft', target='pending')
    def submit_for_review(self):
        """Submit listing after uploading documents"""
        if self.documents.count() == 0:
            raise ValidationError("At least one document required")
    
    @transition(field=status, source='pending', target='under_review')
    def assign_advocate(self, advocate):
        """Assign to advocate for verification"""
        Verification.objects.create(
            property=self,
            advocate=advocate,
            status='pending'
        )
    
    @transition(field=status, source='under_review', target='approved')
    def approve(self):
        """Advocate approves the listing"""
        self.approved_at = timezone.now()
        self.expires_at = timezone.now() + timedelta(days=90)  # Listing valid for 90 days
    
    @transition(field=status, source='under_review', target='changes_requested')
    def request_changes(self, remarks):
        """Advocate requests document changes"""
        pass
    
    @transition(field=status, source=['under_review', 'changes_requested'], target='rejected')
    def reject(self, reason):
        """Advocate rejects the listing"""
        pass
```

#### 2.2 Property Images Model
```python
class PropertyImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField()  # Cloudinary URL
    thumbnail_url = models.URLField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
```

#### 2.3 Document Model
```python
class Document(models.Model):
    DOC_TYPES = [
        ('ec', 'Encumbrance Certificate (EC)'),
        ('mother_deed', 'Mother Deed'),
        ('khata', 'Khata Certificate'),
        ('rtc', 'RTC (Pahani)'),
        ('conversion_order', 'Conversion Order'),
        ('sale_deed', 'Sale Deed'),
        ('rera_cert', 'RERA Certificate'),
        ('tax_receipt', 'Property Tax Receipt'),
        ('plan_approval', 'Building Plan Approval'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=30, choices=DOC_TYPES)
    s3_key = models.CharField(max_length=500)  # S3 object key (used to generate presigned URLs)
    file_url = models.URLField()  # HTTPS URL (not s3://)
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()  # bytes
    mime_type = models.CharField(max_length=100)
    checksum = models.CharField(max_length=64)  # SHA-256
    uploaded_at = models.DateTimeField(auto_now_add=True)
```

#### 2.4 Verification Model
```python
class Verification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='verifications')
    advocate = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_verifications')
    
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('changes_requested', 'Changes Requested'),
    ], default='pending')
    
    remarks = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Document-level feedback
    document_feedback = models.JSONField(default=dict)
    # Example: {"ec": {"status": "approved"}, "khata": {"status": "rejected", "reason": "Expired"}}
    
    assigned_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-assigned_at']
```

#### 2.5 Property API Endpoints
- [ ] `GET /api/v1/properties/` — List with filters (type, price, location, status)
- [ ] `POST /api/v1/properties/` — Create new listing
- [ ] `GET /api/v1/properties/{id}/` — Property detail
- [ ] `PATCH /api/v1/properties/{id}/` — Update listing
- [ ] `DELETE /api/v1/properties/{id}/` — Delete listing
- [ ] `POST /api/v1/properties/{id}/submit/` — Submit for review
- [ ] `GET /api/v1/properties/my-listings/` — User's own listings
- [ ] `GET /api/v1/properties/favorites/` — User's saved properties
- [ ] `POST /api/v1/properties/{id}/favorite/` — Add to favorites
- [ ] `DELETE /api/v1/properties/{id}/favorite/` — Remove from favorites

#### 2.6 Geo Search Implementation
```python
# properties/views.py
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point

class PropertyViewSet(viewsets.ModelViewSet):
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius_km = request.query_params.get('radius', 5)
        
        user_location = Point(float(lng), float(lat), srid=4326)
        
        properties = Property.objects.filter(
            status='approved',
            location__dwithin=(user_location, D(km=float(radius_km)))
        ).annotate(
            distance=Distance('location', user_location)
        ).order_by('distance')
        
        return self.get_paginated_response(
            PropertySerializer(properties, many=True).data
        )
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        
        # Full-text search + geo
        properties = Property.objects.filter(
            status='approved'
        ).annotate(
            rank=SearchRank(
                SearchVector('title', 'description', 'locality'),
                SearchQuery(query)
            )
        ).filter(rank__gte=0.1).order_by('-rank')
        
        return self.get_paginated_response(
            PropertySerializer(properties, many=True).data
        )
```

#### 2.7 Document Upload with S3
```python
# documents/views.py
import boto3
import hashlib

class DocumentViewSet(viewsets.ModelViewSet):
    ALLOWED_MIME_TYPES = {'application/pdf', 'image/jpeg', 'image/png'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    def create(self, request, property_pk=None):
        property = get_object_or_404(Property, pk=property_pk, owner=request.user)

        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=400)

        doc_type = request.data.get('doc_type')

        # Validate file size
        if file.size > self.MAX_FILE_SIZE:
            return Response({'error': 'File too large. Maximum 10MB allowed.'}, status=400)

        # Validate MIME type server-side (ignore client-provided Content-Type)
        import magic
        detected_mime = magic.from_buffer(file.read(2048), mime=True)
        file.seek(0)
        if detected_mime not in self.ALLOWED_MIME_TYPES:
            return Response({'error': 'Invalid file type. Only PDF, JPG, PNG allowed.'}, status=400)

        # Sanitize filename to prevent directory traversal
        import os, re as _re
        safe_name = os.path.basename(file.name)
        safe_name = _re.sub(r'[^\w.\-]', '_', safe_name)

        # Calculate checksum
        sha256 = hashlib.sha256()
        for chunk in file.chunks():
            sha256.update(chunk)
        checksum = sha256.hexdigest()
        file.seek(0)

        # Upload to S3 with server-side encryption
        s3 = boto3.client('s3')
        s3_key = f"documents/{property.id}/{uuid.uuid4()}/{safe_name}"
        s3.upload_fileobj(
            file, settings.AWS_BUCKET_NAME, s3_key,
            ExtraArgs={'ContentType': detected_mime, 'ServerSideEncryption': 'AES256'}
        )

        # Create document record
        document = Document.objects.create(
            property=property,
            doc_type=doc_type,
            s3_key=s3_key,
            file_url=f"https://{settings.AWS_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}",
            file_name=safe_name,
            file_size=file.size,
            mime_type=detected_mime,
            checksum=checksum
        )

        return Response(DocumentSerializer(document).data, status=201)
    
    @action(detail=True, methods=['get'])
    def download_url(self, request, pk=None):
        """Generate presigned URL for document access"""
        document = self.get_object()
        
        # Check permission (owner or assigned advocate)
        if not self.can_access_document(request.user, document):
            raise PermissionDenied()
        
        s3 = boto3.client('s3')
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.AWS_BUCKET_NAME, 'Key': document.s3_key},
            ExpiresIn=1800  # 30 minutes
        )
        
        return Response({'url': url})
```

#### 2.8 Advocate Verification Workflow
```python
# verifications/views.py
class VerificationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdvocate]
    
    def get_queryset(self):
        return Verification.objects.filter(advocate=self.request.user)
    
    @action(detail=False, methods=['get'])
    def queue(self, request):
        """Get pending verifications for this advocate"""
        pending = self.get_queryset().filter(status='pending')
        return Response(VerificationSerializer(pending, many=True).data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        verification = self.get_object()
        verification.status = 'approved'
        verification.reviewed_at = timezone.now()
        verification.save()
        
        # Trigger property status change
        verification.property.approve()
        verification.property.save()
        
        # Notify seller
        send_notification.delay(
            user_id=verification.property.owner.id,
            title="Listing Approved!",
            message=f"Your property '{verification.property.title}' is now live."
        )
        
        return Response({'status': 'approved'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        verification = self.get_object()
        verification.status = 'rejected'
        verification.rejection_reason = request.data.get('reason', '')
        verification.reviewed_at = timezone.now()
        verification.save()
        
        verification.property.reject(verification.rejection_reason)
        verification.property.save()
        
        return Response({'status': 'rejected'})
    
    @action(detail=True, methods=['post'])
    def request_changes(self, request, pk=None):
        verification = self.get_object()
        verification.status = 'changes_requested'
        verification.document_feedback = request.data.get('feedback', {})
        verification.remarks = request.data.get('remarks', '')
        verification.save()
        
        verification.property.request_changes(verification.remarks)
        verification.property.save()
        
        return Response({'status': 'changes_requested'})
```

#### 2.9 Advocate Assignment (Round-Robin)
```python
# verifications/services.py
from django.db.models import Count

def assign_advocate_to_property(property):
    """Assign advocate with least pending workload"""
    advocates = User.objects.filter(
        role='advocate',
        is_active=True,
        city=property.city
    ).annotate(
        pending_count=Count('assigned_verifications', filter=Q(
            assigned_verifications__status='pending'
        ))
    ).order_by('pending_count')
    
    if not advocates.exists():
        raise NoAdvocateAvailable()
    
    advocate = advocates.first()
    property.assign_advocate(advocate)
    property.save()
    
    # Notify advocate
    send_notification.delay(
        user_id=advocate.id,
        title="New Verification Assigned",
        message=f"Property '{property.title}' needs your review."
    )
    
    return advocate
```

### Frontend Tasks

#### 2.10 Property Listing Pages
- [ ] Property list page with infinite scroll
- [ ] Filter sidebar (type, price range, bedrooms, locality)
- [ ] Sort options (price, date, distance)
- [ ] Map view with property markers (react-leaflet)
- [ ] Property card component with image carousel
- [ ] Property detail page with gallery, amenities, location map

#### 2.11 Property Creation Flow
- [ ] Multi-step form wizard
  - Step 1: Basic info (title, type, price, area)
  - Step 2: Location (map picker, address)
  - Step 3: Details (bedrooms, amenities)
  - Step 4: Photos (drag-drop upload, reorder)
  - Step 5: Documents (upload with type selection)
  - Step 6: Review and submit
- [ ] Draft auto-save to localStorage
- [ ] Image upload with preview and crop
- [ ] Document upload with progress indicator

#### 2.12 Seller Dashboard
- [ ] My listings grid/list view
- [ ] Status badges (draft, pending, approved, rejected)
- [ ] Edit listing action
- [ ] View inquiries count
- [ ] Resubmit after changes requested

#### 2.13 Advocate Dashboard
- [ ] Verification queue with filters
- [ ] Property detail view with documents
- [ ] Document viewer (PDF, images)
- [ ] Approve/Reject/Request Changes actions
- [ ] Feedback form for document issues
- [ ] Verification history

### Phase 2 Deliverables
- [x] Property CRUD fully functional
- [x] Image upload to Cloudinary working
- [x] Document upload to S3 working
- [x] Geo search (nearby properties) working
- [x] Full-text search working
- [x] Verification workflow complete
- [x] Advocate can approve/reject listings
- [x] Seller receives status notifications

---

## Phase 3: Communication System (Week 6-7)

### Goals
- Real-time chat between buyers and sellers
- Contact masking until mutual consent
- WhatsApp notification integration
- In-app notifications

### Backend Tasks

#### 3.1 Conversation & Message Models
```python
# conversations/models.py
class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_conversations')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_conversations')
    
    # Contact sharing
    contact_shared = models.BooleanField(default=False)
    contact_shared_at = models.DateTimeField(null=True, blank=True)
    
    # Rate limiting
    buyer_message_count = models.PositiveIntegerField(default=0)
    last_message_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['property', 'buyer']

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)

    content = models.TextField()         # Raw content — NEVER expose via API
    masked_content = models.TextField(blank=True)  # Always serve this via API

    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sent_at']

# IMPORTANT: MessageSerializer must always use 'masked_content' as the
# response field. Never include 'content' in any serializer or API view.
# Only admin/staff can access raw 'content' via Django admin.
```

#### 3.2 Contact Masking Service
```python
# conversations/services.py
import re

class ContactMaskingService:
    PHONE_PATTERNS = [
        r'\b[6-9]\d{9}\b',  # Indian mobile
        r'\b[6-9]\d{4}[\s-]?\d{5}\b',  # With space/dash
        r'\+91[\s-]?[6-9]\d{9}\b',  # With country code
    ]
    
    EMAIL_PATTERN = r'\b[\w.-]+@[\w.-]+\.\w{2,}\b'
    
    @classmethod
    def mask_contacts(cls, content, conversation):
        """Mask phone numbers and emails if contact not shared"""
        if conversation.contact_shared:
            return content
        
        masked = content
        
        # Mask phone numbers
        for pattern in cls.PHONE_PATTERNS:
            masked = re.sub(pattern, '[phone hidden - upgrade to view]', masked)
        
        # Mask emails
        masked = re.sub(cls.EMAIL_PATTERN, '[email hidden]', masked)
        
        return masked
    
    @classmethod
    def contains_contact(cls, content):
        """Check if message contains contact info"""
        for pattern in cls.PHONE_PATTERNS:
            if re.search(pattern, content):
                return True
        if re.search(cls.EMAIL_PATTERN, content):
            return True
        return False
```

#### 3.3 Django Channels WebSocket Consumer
```python
# conversations/consumers.py
import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        self.user = self.scope['user']
        
        # Verify user is part of conversation
        if not await self.is_participant():
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive_json(self, content):
        message_type = content.get('type')
        
        if message_type == 'chat_message':
            await self.handle_chat_message(content)
        elif message_type == 'typing':
            await self.handle_typing(content)
        elif message_type == 'read_receipt':
            await self.handle_read_receipt(content)
    
    async def handle_chat_message(self, content):
        message_text = content['message']
        
        # Rate limiting check
        if not await self.check_rate_limit():
            await self.send_json({
                'type': 'error',
                'message': 'Rate limit exceeded. Please wait.'
            })
            return
        
        # Save message
        message = await self.save_message(message_text)
        
        # Broadcast to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': str(message.id),
                    'content': message.masked_content,
                    'sender_id': str(self.user.id),
                    'sent_at': message.sent_at.isoformat(),
                }
            }
        )
        
        # Send push notification to recipient
        await self.send_push_notification(message)
    
    async def chat_message(self, event):
        await self.send_json(event)
    
    @database_sync_to_async
    def is_participant(self):
        """Check that the connected user is the buyer or seller in this conversation."""
        from django.db.models import Q
        return Conversation.objects.filter(
            id=self.conversation_id
        ).filter(
            Q(buyer=self.user) | Q(seller=self.user)
        ).exists()

    @database_sync_to_async
    def save_message(self, content):
        from django.db import transaction as db_transaction
        from django.db.models import F

        with db_transaction.atomic():
            conversation = Conversation.objects.select_for_update().get(id=self.conversation_id)

            masked_content = ContactMaskingService.mask_contacts(content, conversation)

            message = Message.objects.create(
                conversation=conversation,
                sender=self.user,
                content=content,
                masked_content=masked_content
            )

            # Use atomic update to avoid race condition on buyer_message_count
            Conversation.objects.filter(id=self.conversation_id).update(
                last_message_at=message.sent_at,
                buyer_message_count=F('buyer_message_count') + 1
            )

        return message

    @database_sync_to_async
    def check_rate_limit(self):
        """Max 10 messages per hour to new sellers"""
        conversation = Conversation.objects.get(id=self.conversation_id)
        
        if conversation.contact_shared:
            return True  # No limit after contact shared
        
        if self.user == conversation.seller:
            return True  # No limit for seller
        
        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_count = Message.objects.filter(
            conversation=conversation,
            sender=self.user,
            sent_at__gte=one_hour_ago
        ).count()
        
        return recent_count < 10
```

#### 3.4 Channels Routing
```python
# config/asgi.py
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from conversations.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})

# conversations/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<conversation_id>[0-9a-f-]+)/$', consumers.ChatConsumer.as_asgi()),
]
```

#### 3.5 WhatsApp Notification Integration
```python
# notifications/services.py
import requests

class WhatsAppService:
    API_URL = "https://graph.facebook.com/v17.0/{phone_id}/messages"
    
    def __init__(self):
        self.phone_id = settings.WHATSAPP_PHONE_ID
        self.token = settings.WHATSAPP_ACCESS_TOKEN
    
    def send_template_message(self, to_phone, template_name, parameters):
        """Send WhatsApp template message"""
        payload = {
            "messaging_product": "whatsapp",
            "to": f"91{to_phone}",
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "en"},
                "components": [{
                    "type": "body",
                    "parameters": [{"type": "text", "text": p} for p in parameters]
                }]
            }
        }
        
        response = requests.post(
            self.API_URL.format(phone_id=self.phone_id),
            headers={"Authorization": f"Bearer {self.token}"},
            json=payload
        )
        
        return response.json()
    
    def send_new_inquiry_notification(self, seller, property, buyer_name):
        """Notify seller of new inquiry"""
        self.send_template_message(
            to_phone=seller.phone,
            template_name="new_inquiry",
            parameters=[buyer_name, property.title]
        )
    
    def send_listing_approved_notification(self, seller, property):
        """Notify seller that listing is approved"""
        self.send_template_message(
            to_phone=seller.phone,
            template_name="listing_approved",
            parameters=[property.title]
        )
```

#### 3.6 Celery Beat Scheduled Tasks
```python
# config/celery.py
from celery.schedules import crontab

app.conf.beat_schedule = {
    # Expire listings after 90 days
    'expire-old-listings': {
        'task': 'properties.tasks.expire_listings',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2am
    },
    # Escalate verifications stuck > 7 days
    'escalate-stale-verifications': {
        'task': 'verifications.tasks.escalate_stale_verifications',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9am
    },
    # Expire subscriptions
    'expire-subscriptions': {
        'task': 'payments.tasks.expire_subscriptions',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
    # Send listing renewal reminders (7 days before expiry)
    'listing-renewal-reminders': {
        'task': 'properties.tasks.send_renewal_reminders',
        'schedule': crontab(hour=10, minute=0),
    },
}

# properties/tasks.py
@shared_task
def expire_listings():
    """Mark listings as expired after 90 days."""
    expired = Property.objects.filter(
        status='approved',
        expires_at__lt=timezone.now()
    )
    count = expired.update(status='expired')
    return f"Expired {count} listings"

# verifications/tasks.py
@shared_task
def escalate_stale_verifications():
    """Flag verifications pending for more than 7 days."""
    threshold = timezone.now() - timedelta(days=7)
    stale = Verification.objects.filter(
        status='pending',
        assigned_at__lt=threshold
    )
    for v in stale:
        send_notification.delay(
            user_id=str(v.advocate.id),
            title="Verification Overdue",
            message=f"'{v.property.title}' has been waiting for your review for 7+ days."
        )
    return f"Escalated {stale.count()} verifications"
```

#### 3.7 Celery Tasks for Notifications
```python
# notifications/tasks.py
from celery import shared_task

@shared_task
def send_push_notification(user_id, title, message, data=None):
    """Send FCM push notification"""
    user = User.objects.get(id=user_id)
    
    if not user.fcm_token:
        return
    
    # Firebase Cloud Messaging
    from firebase_admin import messaging
    
    notification = messaging.Message(
        notification=messaging.Notification(title=title, body=message),
        data=data or {},
        token=user.fcm_token
    )
    
    messaging.send(notification)

@shared_task
def send_whatsapp_notification(user_id, template_name, parameters):
    """Send WhatsApp notification"""
    user = User.objects.get(id=user_id)
    
    if not user.phone or not user.whatsapp_opt_in:
        return
    
    whatsapp = WhatsAppService()
    whatsapp.send_template_message(user.phone, template_name, parameters)
```

#### 3.8 Email Notification Service
```python
# requirements.txt addition
# django-anymail==10.2  (supports SendGrid, Mailgun, etc.)

# config/settings/base.py
ANYMAIL = {
    'SENDGRID_API_KEY': env('SENDGRID_API_KEY'),
}
EMAIL_BACKEND = 'anymail.backends.sendgrid.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@belagaviproperty.com'

# notifications/email.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from celery import shared_task

@shared_task
def send_listing_approved_email(user_id, property_id):
    from users.models import User
    from properties.models import Property
    user = User.objects.get(id=user_id)
    prop = Property.objects.get(id=property_id)
    send_mail(
        subject=f"Your listing '{prop.title}' is now live!",
        message=render_to_string('emails/listing_approved.txt', {'property': prop}),
        html_message=render_to_string('emails/listing_approved.html', {'property': prop}),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

@shared_task
def send_otp_email(user_id, otp):
    from users.models import User
    user = User.objects.get(id=user_id)
    send_mail(
        subject="Your OTP for Belagavi Property Connect",
        message=f"Your OTP is {otp}. It expires in 10 minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

# Email templates needed (in templates/emails/):
# - listing_approved.html / .txt
# - listing_rejected.html / .txt
# - payment_confirmed.html / .txt
# - new_inquiry.html / .txt
# - welcome.html / .txt
# - otp_verification.html / .txt
```

### Frontend Tasks

#### 3.9 Chat Interface
- [ ] Conversation list with last message preview
- [ ] Unread message count badges
- [ ] Chat window with message bubbles
- [ ] Real-time message updates (WebSocket)
- [ ] Typing indicator
- [ ] Message read receipts
- [ ] Contact sharing request/accept flow
- [ ] "Contact hidden" placeholder with upgrade prompt

#### 3.10 Notification Center
- [ ] In-app notification dropdown
- [ ] Notification list page
- [ ] Mark as read functionality
- [ ] Push notification opt-in prompt
- [ ] FCM token registration

### Phase 3 Deliverables
- [x] Real-time chat working
- [x] Contact masking functional
- [x] Rate limiting prevents spam
- [x] WhatsApp notifications sending
- [x] Push notifications working
- [x] Typing indicators and read receipts
- [x] Email notifications sending (SendGrid via django-anymail)
- [x] Celery Beat scheduled tasks running (listing expiry, verification escalation)

---

## Phase 4: Payments & PWA (Week 8-9)

### Goals
- Razorpay integration for payments
- Subscription management
- Full PWA with offline support
- Image optimization

### Backend Tasks

#### 4.1 Payment Models
```python
# payments/models.py
class Plan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_days = models.PositiveIntegerField()
    features = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    
    # Limits
    max_contacts_per_month = models.PositiveIntegerField(default=5)
    max_listings = models.PositiveIntegerField(default=1)

class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ])
    
    starts_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    
    # Usage tracking
    contacts_used = models.PositiveIntegerField(default=0)
    listings_used = models.PositiveIntegerField(default=0)

class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    
    # Razorpay
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature = models.CharField(max_length=255, blank=True)
    
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ], default='pending')
    
    # What was purchased
    transaction_type = models.CharField(max_length=30, choices=[
        ('subscription', 'Subscription'),
        ('listing_fee', 'Listing Fee'),
        ('verification_fee', 'Verification Fee'),
        ('featured', 'Featured Listing'),
    ])
    
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### 4.2 Razorpay Integration
```python
# payments/services.py
import razorpay

class RazorpayService:
    def __init__(self):
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
    
    def create_order(self, amount, currency='INR', notes=None):
        """Create Razorpay order"""
        order = self.client.order.create({
            'amount': int(amount * 100),  # Razorpay expects paise
            'currency': currency,
            'notes': notes or {}
        })
        return order
    
    def verify_payment(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """Verify payment signature"""
        try:
            self.client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
            return True
        except razorpay.errors.SignatureVerificationError:
            return False

# payments/views.py
class PaymentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def create_order(self, request):
        """Create Razorpay order for subscription/listing"""
        transaction_type = request.data['type']
        
        if transaction_type == 'subscription':
            plan = Plan.objects.get(slug=request.data['plan'])
            amount = plan.price
        elif transaction_type == 'listing_fee':
            amount = Decimal('500.00')  # Base listing fee
        elif transaction_type == 'verification_fee':
            amount = Decimal('1500.00')
        
        razorpay_service = RazorpayService()
        order = razorpay_service.create_order(
            amount=amount,
            notes={'user_id': str(request.user.id), 'type': transaction_type}
        )
        
        # Save transaction
        transaction = Transaction.objects.create(
            user=request.user,
            amount=amount,
            razorpay_order_id=order['id'],
            transaction_type=transaction_type,
            metadata=request.data
        )
        
        return Response({
            'order_id': order['id'],
            'amount': order['amount'],
            'currency': order['currency'],
            'key': settings.RAZORPAY_KEY_ID
        })
    
    @action(detail=False, methods=['post'])
    def verify(self, request):
        """Verify payment and activate subscription"""
        razorpay_order_id = request.data['razorpay_order_id']
        razorpay_payment_id = request.data['razorpay_payment_id']
        razorpay_signature = request.data['razorpay_signature']
        
        razorpay_service = RazorpayService()

        if not razorpay_service.verify_payment(
            razorpay_order_id, razorpay_payment_id, razorpay_signature
        ):
            return Response({'error': 'Payment verification failed'}, status=400)

        from django.db import transaction as db_transaction

        with db_transaction.atomic():
            # Idempotency guard: atomically move from 'pending' → 'completed' only once
            updated_count = Transaction.objects.filter(
                razorpay_order_id=razorpay_order_id,
                status='pending'  # Guard prevents double-processing
            ).update(
                razorpay_payment_id=razorpay_payment_id,
                razorpay_signature=razorpay_signature,
                status='completed'
            )

            if not updated_count:
                # Already processed (duplicate webhook or concurrent request)
                return Response({'status': 'success'})

            transaction = Transaction.objects.get(razorpay_order_id=razorpay_order_id)

            # Activate subscription if applicable
            if transaction.transaction_type == 'subscription':
                plan = Plan.objects.get(slug=transaction.metadata['plan'])
                Subscription.objects.create(
                    user=request.user,
                    plan=plan,
                    status='active',
                    starts_at=timezone.now(),
                    expires_at=timezone.now() + timedelta(days=plan.duration_days)
                )

        return Response({'status': 'success'})
```

#### 4.3 Razorpay Webhook Handler
```python
# payments/views.py
import hmac, hashlib

class RazorpayWebhookView(APIView):
    authentication_classes = []  # Webhook has no user auth
    permission_classes = []

    def post(self, request):
        # Verify webhook signature
        webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
        signature = request.headers.get('X-Razorpay-Signature', '')
        body = request.body

        expected = hmac.new(
            webhook_secret.encode(), body, hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected, signature):
            return Response({'error': 'Invalid signature'}, status=400)

        event = request.data.get('event')
        payload = request.data.get('payload', {})

        if event == 'payment.captured':
            razorpay_payment_id = payload['payment']['entity']['id']
            razorpay_order_id = payload['payment']['entity']['order_id']
            # Trigger same completion logic as /verify endpoint
            process_successful_payment.delay(razorpay_order_id, razorpay_payment_id)

        elif event == 'payment.failed':
            razorpay_order_id = payload['payment']['entity']['order_id']
            Transaction.objects.filter(
                razorpay_order_id=razorpay_order_id,
                status='pending'
            ).update(status='failed')

        return Response({'status': 'ok'})

# Add to urls.py:
# path('api/v1/payments/webhook/', RazorpayWebhookView.as_view()),
```

### Frontend Tasks

#### 4.5 PWA Configuration
```javascript
// vite.config.js
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png'],
      manifest: {
        name: 'Belagavi Property Connect',
        short_name: 'PropConnect',
        description: 'P2P Real Estate Marketplace',
        theme_color: '#028090',
        background_color: '#ffffff',
        display: 'standalone',
        start_url: '/',
        icons: [
          { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icon-512.png', sizes: '512x512', type: 'image/png' },
          { src: '/icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\.belagaviproperty\.com\/api\/v1\/properties/,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'api-properties',
              expiration: { maxEntries: 100, maxAgeSeconds: 3600 }
            }
          },
          {
            urlPattern: /^https:\/\/res\.cloudinary\.com/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'property-images',
              expiration: { maxEntries: 200, maxAgeSeconds: 86400 * 30 }
            }
          }
        ]
      }
    })
  ]
})
```

#### 4.6 Offline Storage with IndexedDB
```javascript
// src/utils/offlineStorage.js
import { openDB } from 'idb';

const dbPromise = openDB('propconnect', 1, {
  upgrade(db) {
    db.createObjectStore('favorites', { keyPath: 'id' });
    db.createObjectStore('recentViews', { keyPath: 'id' });
    db.createObjectStore('savedSearches', { keyPath: 'id' });
    db.createObjectStore('drafts', { keyPath: 'id' });
  }
});

export const offlineStorage = {
  async saveFavorite(property) {
    const db = await dbPromise;
    await db.put('favorites', { ...property, savedAt: Date.now() });
  },
  
  async getFavorites() {
    const db = await dbPromise;
    return db.getAll('favorites');
  },
  
  async addRecentView(property) {
    const db = await dbPromise;
    const views = await db.getAll('recentViews');
    
    // Keep only last 20
    if (views.length >= 20) {
      await db.delete('recentViews', views[0].id);
    }
    
    await db.put('recentViews', { ...property, viewedAt: Date.now() });
  },
  
  async saveDraft(draft) {
    const db = await dbPromise;
    await db.put('drafts', { ...draft, updatedAt: Date.now() });
  },
  
  async getDraft(id) {
    const db = await dbPromise;
    return db.get('drafts', id);
  }
};
```

#### 4.7 Image Optimization
```javascript
// src/utils/imageOptimization.js
export const getOptimizedImageUrl = (cloudinaryUrl, options = {}) => {
  const { width = 400, quality = 'auto', format = 'auto' } = options;
  
  // Cloudinary transformation
  const transformation = `w_${width},q_${quality},f_${format}`;
  
  return cloudinaryUrl.replace('/upload/', `/upload/${transformation}/`);
};

// Usage in PropertyCard
const PropertyCard = ({ property }) => {
  const thumbnailUrl = getOptimizedImageUrl(property.images[0]?.url, {
    width: 400,
    quality: 'auto',
    format: 'webp'
  });
  
  return (
    <img
      src={thumbnailUrl}
      alt={property.title}
      loading="lazy"
      decoding="async"
    />
  );
};
```

#### 4.8 Payment Flow UI
- [ ] Pricing/plans page
- [ ] Plan comparison table
- [ ] Razorpay checkout integration
- [ ] Payment success/failure pages
- [ ] Subscription status in profile
- [ ] Invoice download

### Phase 4 Deliverables
- [x] Razorpay payments working
- [x] Subscription management complete
- [x] PWA installable on mobile
- [x] Offline favorites/drafts working
- [x] Images optimized (WebP, lazy load)
- [x] Service worker caching strategies

---

## Phase 5: Launch Preparation (Week 10)

### Goals
- Production deployment
- Performance optimization
- Security hardening
- QA and bug fixes

### Infrastructure Tasks

#### 5.1 CI/CD Pipeline (GitHub Actions)
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgis/postgis:15-3.3
        env:
          POSTGRES_DB: propconnect_test
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports: ['5432:5432']
      redis:
        image: redis:7
        ports: ['6379:6379']

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run linting
        run: flake8 . --max-line-length=120
      - name: Run tests
        env:
          DATABASE_URL: postgis://postgres:postgres@localhost:5432/propconnect_test
          REDIS_URL: redis://localhost:6379/0
          SECRET_KEY: test-secret-key
        run: pytest --cov=. --cov-report=xml --cov-fail-under=70
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: cd frontend && npm ci
      - run: cd frontend && npm run lint
      - run: cd frontend && npm run test -- --run
      - run: cd frontend && npm run build

  deploy:
    needs: [backend, frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to production
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: deploy
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: bash /var/www/propconnect/deploy.sh
```

#### 5.2 Custom Django Admin
```python
# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'phone', 'role', 'is_phone_verified', 'is_active', 'date_joined']
    list_filter = ['role', 'is_phone_verified', 'is_active']
    search_fields = ['email', 'phone', 'first_name', 'last_name']
    ordering = ['-date_joined']

# properties/admin.py
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'property_type', 'status', 'city', 'price', 'created_at']
    list_filter = ['status', 'property_type', 'city']
    search_fields = ['title', 'locality', 'owner__email']
    actions = ['approve_listings', 'reject_listings']
    readonly_fields = ['created_at', 'updated_at', 'approved_at']

    def approve_listings(self, request, queryset):
        for prop in queryset.filter(status='under_review'):
            prop.approve()
            prop.save()
    approve_listings.short_description = "Approve selected listings"

# verifications/admin.py
@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ['property', 'advocate', 'status', 'assigned_at', 'reviewed_at']
    list_filter = ['status']
    search_fields = ['property__title', 'advocate__email']
    ordering = ['-assigned_at']

# payments/admin.py
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'transaction_type', 'status', 'created_at']
    list_filter = ['status', 'transaction_type']
    search_fields = ['user__email', 'razorpay_order_id', 'razorpay_payment_id']
    readonly_fields = ['razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature']
```

#### 5.3 API Documentation (drf-spectacular)
```python
# requirements.txt addition: drf-spectacular==0.27.0

# config/settings/base.py
INSTALLED_APPS += ['drf_spectacular']

REST_FRAMEWORK = {
    ...
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Belagavi Property Connect API',
    'DESCRIPTION': 'P2P Real Estate Marketplace',
    'VERSION': '1.0.0',
}

# config/urls.py
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns += [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

#### 5.4 Server Setup (Hetzner)
```bash
# Initial server setup
ssh root@your-server-ip

# Create deploy user
adduser deploy
usermod -aG sudo deploy

# Install dependencies
apt update && apt upgrade -y
apt install -y python3.11 python3.11-venv python3-pip nginx redis-server
apt install -y postgresql-15 postgresql-15-postgis-3
apt install -y certbot python3-certbot-nginx

# Install Node.js (for frontend build)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
apt install -y nodejs

# Setup PostgreSQL
sudo -u postgres createuser propconnect
sudo -u postgres createdb propconnect -O propconnect
sudo -u postgres psql -c "ALTER USER propconnect WITH PASSWORD 'secure_password';"
sudo -u postgres psql -d propconnect -c "CREATE EXTENSION postgis;"
```

#### 5.5 Django Production Settings
```python
# config/settings/prod.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

DEBUG = False
ALLOWED_HOSTS = ['belagaviproperty.com', 'www.belagaviproperty.com']

# Security
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 60,
    }
}

# Caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': env('REDIS_URL'),
    }
}

# Sentry
sentry_sdk.init(
    dsn=env('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False
)
```

#### 5.6 Nginx Configuration
```nginx
# /etc/nginx/sites-available/propconnect
upstream django {
    server 127.0.0.1:8000;
}

upstream channels {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name belagaviproperty.com www.belagaviproperty.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name belagaviproperty.com www.belagaviproperty.com;
    
    ssl_certificate /etc/letsencrypt/live/belagaviproperty.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/belagaviproperty.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml;
    
    # Frontend (React)
    location / {
        root /var/www/propconnect/frontend/dist;
        try_files $uri /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # API
    location /api/ {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket
    location /ws/ {
        proxy_pass http://channels;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
    
    # Django admin
    location /admin/ {
        proxy_pass http://django;
        proxy_set_header Host $host;
    }
    
    # Static files (Django)
    location /static/ {
        alias /var/www/propconnect/backend/staticfiles/;
        expires 1y;
    }
}
```

#### 5.7 Systemd Services
```ini
# /etc/systemd/system/propconnect.service
[Unit]
Description=PropConnect Django
After=network.target

[Service]
User=deploy
Group=deploy
WorkingDirectory=/var/www/propconnect/backend
ExecStart=/var/www/propconnect/venv/bin/gunicorn config.wsgi:application -w 4 -b 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target

# /etc/systemd/system/propconnect-channels.service
[Unit]
Description=PropConnect Channels
After=network.target

[Service]
User=deploy
Group=deploy
WorkingDirectory=/var/www/propconnect/backend
ExecStart=/var/www/propconnect/venv/bin/daphne -b 127.0.0.1 -p 8001 config.asgi:application
Restart=always

[Install]
WantedBy=multi-user.target

# /etc/systemd/system/propconnect-celery.service
[Unit]
Description=PropConnect Celery
After=network.target

[Service]
User=deploy
Group=deploy
WorkingDirectory=/var/www/propconnect/backend
ExecStart=/var/www/propconnect/venv/bin/celery -A config worker -l info
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 5.8 Deployment Script
```bash
#!/bin/bash
# deploy.sh

set -e

echo "🚀 Deploying PropConnect..."

# Pull latest code
cd /var/www/propconnect
git pull origin main

# Backend
echo "📦 Installing backend dependencies..."
source venv/bin/activate
pip install -r requirements.txt

echo "🗃️ Running migrations..."
python manage.py migrate --noinput

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Frontend
echo "🎨 Building frontend..."
cd frontend
npm ci
npm run build

# Restart services
echo "🔄 Restarting services..."
sudo systemctl restart propconnect
sudo systemctl restart propconnect-channels
sudo systemctl restart propconnect-celery
sudo systemctl reload nginx

echo "✅ Deployment complete!"
```

### QA Checklist

#### 5.9 Functionality Testing
- [ ] User registration flow
- [ ] Login/logout/password reset
- [ ] Property listing creation (all steps)
- [ ] Image upload
- [ ] Document upload
- [ ] Advocate verification flow
- [ ] Chat messaging
- [ ] Payment flow
- [ ] Search and filters
- [ ] Map functionality
- [ ] Mobile responsiveness

#### 5.10 Performance Testing
- [ ] Lighthouse score > 90 (Performance)
- [ ] First Contentful Paint < 1.5s
- [ ] Time to Interactive < 3s
- [ ] Core Web Vitals passing
- [ ] API response times < 200ms
- [ ] Image loading optimized

#### 5.11 Security Testing
- [ ] HTTPS enforced
- [ ] CORS configured correctly
- [ ] Rate limiting working
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CSRF protection
- [ ] JWT token security
- [ ] File upload validation

### Phase 5 Deliverables
- [x] Production server configured
- [x] SSL certificates installed
- [x] All services running (Gunicorn, Daphne, Celery, Celery Beat)
- [x] Monitoring set up (Sentry, UptimeRobot)
- [x] Backup strategy in place (daily pg_dump to S3)
- [x] QA checklist complete
- [x] Deployment script working
- [x] CI/CD pipeline running on GitHub Actions
- [x] Swagger API docs live at /api/docs/
- [x] Custom Django admin configured

---

## Phase 6: Launch & Growth (Ongoing)

### Week 1-2: Soft Launch

#### 6.1 Seed Content
- [ ] Partner with 5-10 local builders
- [ ] Get 50+ verified listings
- [ ] Onboard 2-3 advocates

#### 6.2 Initial Marketing
- [ ] Google My Business listing
- [ ] Facebook page + initial posts
- [ ] WhatsApp broadcast to local groups
- [ ] Local newspaper ad (optional)

### Week 3-4: Public Launch

#### 6.3 Marketing Push
- [ ] Facebook/Instagram ads (₹500/day)
- [ ] Google Ads for "property in Belagavi"
- [ ] Referral program launch
- [ ] Press release to local media

#### 6.4 Metrics to Track
| Metric | Target (Month 1) |
|--------|------------------|
| Registered users | 500 |
| Verified listings | 100 |
| Daily active users | 50 |
| Conversations started | 200 |
| Successful contacts | 50 |

### Month 2-3: Iteration

#### 6.5 Feature Additions
- [ ] Kannada language support
- [ ] Price trend graphs
- [ ] Similar properties recommendation
- [ ] Builder profile pages
- [ ] Area guides (localities)

#### 6.6 SEO Optimization
- [ ] Property detail pages indexable
- [ ] Locality landing pages
- [ ] Blog with local real estate content
- [ ] Schema markup for properties

### Month 4-6: Expansion Prep

#### 6.7 Multi-City Architecture
- [ ] City configuration model
- [ ] Subdomain routing (hubli.belagaviproperty.com)
- [ ] City-specific advocates
- [ ] Localized pricing

#### 6.8 Next City: Hubli-Dharwad
- [ ] Market research
- [ ] Builder partnerships
- [ ] Advocate recruitment
- [ ] Soft launch

---

## Testing Strategy

### Backend (pytest + pytest-django)

```python
# requirements-dev.txt
pytest==7.4.4
pytest-django==4.7.0
pytest-asyncio==0.21.3
factory-boy==3.3.0
faker==21.0.0
coverage==7.3.4

# conftest.py
import pytest
from rest_framework.test import APIClient
from users.tests.factories import UserFactory

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def buyer(db):
    return UserFactory(role='buyer', is_phone_verified=True)

@pytest.fixture
def seller(db):
    return UserFactory(role='seller', is_phone_verified=True)

@pytest.fixture
def advocate(db):
    return UserFactory(role='advocate', is_active=True)

@pytest.fixture
def auth_client(api_client, buyer):
    api_client.force_authenticate(user=buyer)
    return api_client
```

```python
# users/tests/factories.py
import factory
from factory.django import DjangoModelFactory
from users.models import User

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f'user{n}@example.com')
    phone = factory.Sequence(lambda n: f'9{n:09d}')
    role = 'buyer'
    is_active = True
    is_phone_verified = True

# properties/tests/factories.py
class PropertyFactory(DjangoModelFactory):
    class Meta:
        model = Property

    title = factory.Faker('sentence', nb_words=4)
    property_type = 'apartment'
    price = factory.Faker('pydecimal', min_value=500000, max_value=5000000, right_digits=2)
    area_sqft = factory.Faker('pyint', min_value=500, max_value=3000)
    location = Point(74.4977, 15.8497)  # Belagavi center
    address = factory.Faker('address')
    locality = 'Tilakwadi'
    status = 'draft'
    owner = factory.SubFactory(UserFactory, role='seller')
```

```python
# properties/tests/test_views.py
import pytest
from django.urls import reverse

@pytest.mark.django_db
class TestPropertyCreation:
    def test_seller_can_create_property(self, auth_client_seller, seller):
        url = reverse('property-list')
        data = {
            'title': 'Test Apartment',
            'property_type': 'apartment',
            'price': '1500000.00',
            'area_sqft': 1000,
            'lat': 15.8497, 'lng': 74.4977,
            'address': '123 Test Street',
            'locality': 'Tilakwadi',
        }
        response = auth_client_seller.post(url, data)
        assert response.status_code == 201
        assert response.data['status'] == 'draft'

    def test_buyer_cannot_create_property(self, auth_client, buyer):
        url = reverse('property-list')
        response = auth_client.post(url, {})
        assert response.status_code == 403

# verifications/tests/test_workflow.py
@pytest.mark.django_db
class TestVerificationWorkflow:
    def test_full_approval_flow(self, seller, advocate, db):
        prop = PropertyFactory(owner=seller, status='draft')
        DocumentFactory(property=prop)

        prop.submit_for_review()
        prop.assign_advocate(advocate)
        prop.save()

        verification = Verification.objects.get(property=prop)
        verification.status = 'approved'
        verification.save()

        prop.approve()
        prop.save()

        assert prop.status == 'approved'
        assert prop.approved_at is not None
        assert prop.expires_at is not None
```

### Frontend (Vitest + React Testing Library)
```bash
npm install -D vitest @testing-library/react @testing-library/user-event @testing-library/jest-dom jsdom
```

```javascript
// src/features/auth/LoginForm.test.jsx
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LoginForm } from './LoginForm'

test('shows validation error for empty phone', async () => {
  render(<LoginForm />)
  await userEvent.click(screen.getByRole('button', { name: /login/i }))
  expect(screen.getByText(/phone is required/i)).toBeInTheDocument()
})

// src/utils/contactMasking.test.js
test('masks phone number in message', () => {
  expect(maskContacts('Call me on 9876543210')).toBe('Call me on [phone hidden]')
})
```

### Coverage Targets
| Layer | Minimum Coverage |
|-------|-----------------|
| Backend (pytest) | 70% |
| API endpoints | 90% (critical paths) |
| Payment flows | 100% |
| Frontend (Vitest) | 60% |

---

## Tech Debt & Future Improvements

### Performance
- [ ] Implement Redis caching for property lists
- [ ] Add Elasticsearch for full-text search (when >5000 properties)
- [ ] CDN for API responses (CloudFlare Workers)
- [ ] Database read replicas

### Features
- [ ] Video tours for properties
- [ ] Virtual staging with AI
- [ ] Mortgage calculator
- [ ] Legal document templates
- [ ] Automated EC verification (Kaveri API)

### Infrastructure
- [ ] Move to Kubernetes (when scaling beyond single VPS)
- [x] CI/CD pipeline (GitHub Actions) — implemented in Phase 5
- [x] Automated testing (pytest, Vitest) — implemented in Testing Strategy section
- [ ] Blue-green deployments
- [ ] pgBouncer connection pooling
- [ ] Database read replica for reporting queries
- [ ] CDN (CloudFlare) in front of API

---

## Appendix

### A. Environment Variables

```bash
# .env.example

# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=belagaviproperty.com,www.belagaviproperty.com

# Database
DB_NAME=propconnect
DB_USER=propconnect
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# AWS S3
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_BUCKET_NAME=propconnect-documents
AWS_REGION=ap-south-1

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud
CLOUDINARY_API_KEY=your-key
CLOUDINARY_API_SECRET=your-secret

# Razorpay
RAZORPAY_KEY_ID=rzp_live_xxx
RAZORPAY_KEY_SECRET=your-secret

# WhatsApp
WHATSAPP_PHONE_ID=your-phone-id
WHATSAPP_ACCESS_TOKEN=your-token

# Firebase (Push Notifications)
FIREBASE_CREDENTIALS_PATH=/path/to/firebase-credentials.json

# Sentry
SENTRY_DSN=https://xxx@sentry.io/xxx
```

### B. Package Versions

```txt
# requirements.txt
Django==4.2.8
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.1
django-filter==23.5
django-fsm==2.8.1
channels==4.0.0
channels-redis==4.2.0
celery==5.3.4
celery[redis]==5.3.4          # Celery Beat scheduler
redis==5.0.1
psycopg2-binary==2.9.9
boto3==1.34.0
razorpay==1.4.1
gunicorn==21.2.0
daphne==4.0.0
sentry-sdk==1.38.0
python-decouple==3.8
Pillow==10.1.0
django-anymail[sendgrid]==10.2  # Email notifications
python-magic==0.4.27            # Server-side MIME validation for uploads
drf-spectacular==0.27.0         # OpenAPI/Swagger docs

# requirements-dev.txt
pytest==7.4.4
pytest-django==4.7.0
pytest-asyncio==0.21.3
factory-boy==3.3.0
faker==21.0.0
coverage==7.3.4
flake8==6.1.0
```

```json
// package.json (frontend)
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "@tanstack/react-query": "^5.14.0",
    "zustand": "^4.4.7",
    "axios": "^1.6.2",
    "react-hook-form": "^7.49.0",
    "zod": "^3.22.4",
    "@hookform/resolvers": "^3.3.2",
    "react-leaflet": "^4.2.1",
    "idb": "^8.0.0",
    "react-helmet-async": "^2.0.4"
  },
  "devDependencies": {
    "vite": "^5.0.10",
    "@vitejs/plugin-react": "^4.2.1",
    "vite-plugin-pwa": "^0.17.4",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "vitest": "^1.1.0",
    "@testing-library/react": "^14.1.2",
    "@testing-library/user-event": "^14.5.2",
    "@testing-library/jest-dom": "^6.1.6",
    "jsdom": "^23.0.1",
    "eslint": "^8.56.0",
    "@eslint/js": "^8.56.0"
  }
}
```

---

## Contact & Support

**Project:** Belagavi Property Connect  
**Stack:** Django 4.2 + React 18 + PostgreSQL/PostGIS  
**Target Launch:** Q2 2026  

---

*Document Version: 1.1*
*Last Updated: March 2026*

### Changelog v1.1
- Fixed `Document` model: added `s3_key` field; corrected `file_url` to use HTTPS (not `s3://`)
- Fixed `DocumentViewSet.create`: added file size limit (10MB), server-side MIME validation, filename sanitization, S3 server-side encryption
- Fixed `ChatConsumer`: implemented missing `is_participant()` method; fixed race condition in `buyer_message_count` using atomic `update()`
- Fixed payment `verify` endpoint: added idempotency guard using atomic filter-and-update
- Added `SoftDeleteModel` mixin for Property and other models
- Added GiST spatial index and `expires_at` field to Property model
- Added API rate limiting (DRF throttling) in Phase 1
- Added standardized error response format (custom exception handler)
- Added `is_participant()` WebSocket auth method
- Added Celery Beat scheduled tasks (listing expiry, verification escalation, subscription expiry)
- Added Email notification service (django-anymail + SendGrid)
- Added Razorpay webhook handler
- Added full Testing Strategy section (pytest + Vitest, factories, coverage targets)
- Added CI/CD pipeline (GitHub Actions) in Phase 5
- Added Custom Django Admin configuration
- Added API documentation (drf-spectacular/Swagger)
- Updated requirements.txt with all new packages
