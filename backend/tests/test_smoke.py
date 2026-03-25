"""
Smoke tests — ensure core models, views, and tasks import without errors
and basic API endpoints return expected status codes.
"""
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestPublicEndpoints:
    def test_plans_endpoint_returns_200(self, client):
        url = reverse('payment-plans')
        response = client.get(url)
        assert response.status_code == 200

    def test_plans_returns_four_plans(self, client):
        url = reverse('payment-plans')
        response = client.get(url)
        data = response.json()
        assert len(data) == 4
        codes = {p['code'] for p in data}
        assert codes == {'free', 'basic', 'pro', 'builder'}

    def test_swagger_schema_accessible(self, client):
        url = reverse('schema')
        response = client.get(url)
        assert response.status_code == 200

    def test_notification_list_requires_auth(self, client):
        url = reverse('notification-list')
        response = client.get(url)
        assert response.status_code == 401

    def test_conversation_list_requires_auth(self, client):
        url = '/api/v1/conversations/'
        response = client.get(url)
        assert response.status_code == 401


@pytest.mark.django_db
class TestUserRegistration:
    def test_register_valid_user(self, client):
        url = reverse('auth-register')
        payload = {
            'email': 'testuser@example.com',
            'username': 'testuser',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '9876543210',
            'role': 'buyer',
        }
        response = client.post(url, payload, content_type='application/json')
        assert response.status_code == 201
        data = response.json()
        assert data['user']['email'] == 'testuser@example.com'
        assert 'access' in data
        assert 'password' not in data['user']

    def test_register_duplicate_email_fails(self, client):
        url = reverse('auth-register')
        payload = {
            'email': 'dup@example.com',
            'username': 'dupuser',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'first_name': 'Dup',
            'last_name': 'User',
            'phone': '9876543211',
            'role': 'buyer',
        }
        client.post(url, payload, content_type='application/json')
        response = client.post(url, payload, content_type='application/json')
        assert response.status_code == 400

    def test_login_returns_tokens(self, client, django_user_model):
        django_user_model.objects.create_user(
            username='loginuser',
            email='login@example.com',
            password='TestPass456!',
            phone='9000000001',
            role='buyer',
        )
        url = reverse('auth-login')
        response = client.post(
            url,
            {'username': 'loginuser', 'password': 'TestPass456!'},
            content_type='application/json',
        )
        assert response.status_code == 200
        data = response.json()
        assert 'access' in data
        assert 'refresh' in data


@pytest.mark.django_db
class TestPaymentPlans:
    def test_free_plan_has_zero_price(self, client):
        url = reverse('payment-plans')
        data = client.get(url).json()
        free = next(p for p in data if p['code'] == 'free')
        assert free['price_paise'] == 0

    def test_builder_plan_includes_featured(self, client):
        url = reverse('payment-plans')
        data = client.get(url).json()
        builder = next(p for p in data if p['code'] == 'builder')
        assert builder['is_featured_included'] is True


class FakeConversation:
    def __init__(self, contact_shared=False):
        self.contact_shared = contact_shared


class TestContactMasking:
    def test_phone_numbers_are_masked(self):
        from conversations.services import ContactMaskingService
        text = 'Call me at 9876543210 or +91 9876543210'
        masked = ContactMaskingService.mask(text, FakeConversation(contact_shared=False))
        assert '9876543210' not in masked
        assert 'hidden' in masked

    def test_email_is_masked(self):
        from conversations.services import ContactMaskingService
        text = 'Email me at seller@example.com'
        masked = ContactMaskingService.mask(text, FakeConversation(contact_shared=False))
        assert 'seller@example.com' not in masked

    def test_no_masking_when_contact_shared(self):
        from conversations.services import ContactMaskingService
        text = 'Call me at 9876543210'
        result = ContactMaskingService.mask(text, FakeConversation(contact_shared=True))
        assert result == text
