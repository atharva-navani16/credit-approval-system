from django.apps import AppConfig

class CreditAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'credit_app'
    
    def ready(self):
        import credit_app.tasks 