import re


class ContactMaskingService:
    PHONE_PATTERNS = [
        r'\b[6-9]\d{9}\b',
        r'\b[6-9]\d{4}[\s\-]\d{5}\b',
        r'\+91[\s\-]?[6-9]\d{9}\b',
    ]
    EMAIL_PATTERN = r'\b[\w.\-]+@[\w.\-]+\.\w{2,}\b'
    MASK_PHONE = '[phone hidden — share contact to view]'
    MASK_EMAIL = '[email hidden]'

    @classmethod
    def mask(cls, content: str, conversation) -> str:
        if conversation.contact_shared:
            return content
        masked = content
        for pattern in cls.PHONE_PATTERNS:
            masked = re.sub(pattern, cls.MASK_PHONE, masked)
        masked = re.sub(cls.EMAIL_PATTERN, cls.MASK_EMAIL, masked)
        return masked

    @classmethod
    def contains_contact(cls, content: str) -> bool:
        for pattern in cls.PHONE_PATTERNS:
            if re.search(pattern, content):
                return True
        return bool(re.search(cls.EMAIL_PATTERN, content))
