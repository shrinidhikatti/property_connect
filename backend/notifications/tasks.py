import logging
import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def _create_notification(user_id, notif_type, title, message, data=None):
    """Helper to persist an in-app notification."""
    from users.models import User
    from .models import Notification
    try:
        user = User.objects.get(id=user_id)
        Notification.objects.create(
            user=user,
            notif_type=notif_type,
            title=title,
            message=message,
            data=data or {},
        )
    except Exception as e:
        logger.error(f'Failed to create notification: {e}')


@shared_task(bind=True, max_retries=3)
def send_notification(self, user_id, notif_type, title, message, data=None):
    """Create in-app notification + optionally send WhatsApp/push."""
    _create_notification(user_id, notif_type, title, message, data)
    # WhatsApp and FCM push would be added here with real credentials


@shared_task(bind=True, max_retries=3)
def send_whatsapp(self, phone, template_name, parameters):
    if not settings.WHATSAPP_ACCESS_TOKEN or not settings.WHATSAPP_PHONE_ID:
        logger.info(f'[DEV] WhatsApp skipped — no credentials. Template: {template_name}, params: {parameters}')
        return

    url = f'https://graph.facebook.com/v17.0/{settings.WHATSAPP_PHONE_ID}/messages'
    payload = {
        'messaging_product': 'whatsapp',
        'to': f'91{phone}',
        'type': 'template',
        'template': {
            'name': template_name,
            'language': {'code': 'en'},
            'components': [{'type': 'body', 'parameters': [{'type': 'text', 'text': p} for p in parameters]}],
        },
    }
    try:
        resp = requests.post(
            url,
            headers={'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}'},
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
    except Exception as exc:
        logger.error(f'WhatsApp send failed: {exc}')
        raise self.retry(exc=exc, countdown=60)


# ─── Scheduled tasks (run via Celery Beat) ────────────────────────────────────

@shared_task
def expire_listings():
    """Mark approved listings as expired after 90 days."""
    from properties.models import Property
    from django_fsm import can_proceed
    expired = Property.objects.filter(status='approved', expires_at__lt=timezone.now())
    count = 0
    for prop in expired:
        try:
            prop.expire()
            prop.save()
            count += 1
        except Exception as e:
            logger.warning(f'Could not expire {prop.id}: {e}')
    logger.info(f'Expired {count} listings')
    return count


@shared_task
def escalate_stale_verifications():
    """Notify advocate if verification pending > 7 days."""
    from datetime import timedelta
    from verifications.models import Verification
    threshold = timezone.now() - timedelta(days=7)
    stale = Verification.objects.filter(status='pending', assigned_at__lt=threshold)
    for v in stale:
        send_notification.delay(
            str(v.advocate_id),
            'verification_assigned',
            'Verification Overdue',
            f"'{v.property.title}' has been awaiting review for over 7 days.",
            {'property_id': str(v.property_id)},
        )
    return stale.count()


@shared_task
def expire_subscriptions():
    """Mark active subscriptions as expired."""
    from payments.models import Subscription
    expired = Subscription.objects.filter(status='active', expires_at__lt=timezone.now())
    count = expired.update(status='expired')
    logger.info(f'Expired {count} subscriptions')
    return count


@shared_task
def send_renewal_reminders():
    """Remind sellers 7 days before listing expiry."""
    from datetime import timedelta
    from properties.models import Property
    window_start = timezone.now()
    window_end = timezone.now() + timedelta(days=7)
    expiring = Property.objects.filter(status='approved', expires_at__range=(window_start, window_end))
    for prop in expiring:
        send_notification.delay(
            str(prop.owner_id),
            'system',
            'Your listing expires soon',
            f"'{prop.title}' will expire in 7 days. Renew to keep it visible.",
            {'property_id': str(prop.id)},
        )
    return expiring.count()
