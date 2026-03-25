import logging
from django.db.models import Count, Q
from users.models import User

logger = logging.getLogger(__name__)


class NoAdvocateAvailable(Exception):
    pass


def assign_advocate_to_property(prop):
    """Assign the advocate with the least pending workload in the same city."""
    advocates = User.objects.filter(
        role='advocate',
        is_active=True,
    ).annotate(
        pending_count=Count(
            'assigned_verifications',
            filter=Q(assigned_verifications__status='pending')
        )
    ).order_by('pending_count')

    if not advocates.exists():
        logger.warning(f'No advocates available for property {prop.id}')
        raise NoAdvocateAvailable('No advocates are available. Admin has been notified.')

    advocate = advocates.first()
    prop.assign_advocate(advocate)
    prop.save()

    logger.info(f'Assigned advocate {advocate.email} to property {prop.id}')
    return advocate
