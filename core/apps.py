"""Application configuration for the core app."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Django app config for core."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
