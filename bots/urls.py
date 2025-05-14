from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'bots'

# Роутер для CRUD по моделям
router = DefaultRouter()
router.register(r'bots', views.BotViewSet)
router.register(r'blocks', views.BlockViewSet)
router.register(r'block_connections', views.BlockConnectionViewSet)
router.register(r'data_fields', views.BotDataCaptureViewSet)
router.register(r'menu_buttons', views.MenuButtonViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # Получение/сохранение структуры бота
    path('<int:bot_id>/structure/', views.BotStructureView.as_view(), name='bot-structure'),
    path('<int:bot_id>/save_structure/', views.BotStructureView.as_view(), name='bot-save-structure'),

    # Получение/обновление токена бота
    path('<int:bot_id>/token/', views.BotTokenView.as_view(), name='bot-token'),
]