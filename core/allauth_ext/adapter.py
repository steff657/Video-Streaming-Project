import logging

from allauth.account.adapter import DefaultAccountAdapter


logger = logging.getLogger(__name__)


class ResilientAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        try:
            super().send_mail(template_prefix, email, context)
        except Exception:
            logger.exception(
                "Failed to send account email '%s' to %s",
                template_prefix,
                email,
            )
