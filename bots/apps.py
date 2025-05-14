from django.apps import AppConfig

# Конфигурация приложения bots
class BotsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bots'
    verbose_name = "Боты и блоки"  # Отображение имени в Django Admin
