from django.apps import AppConfig

# Конфигурация приложения API
class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'