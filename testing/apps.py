from django.apps import AppConfig


class TestingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "testing"
    
    def ready(self):
        import testing.signals
