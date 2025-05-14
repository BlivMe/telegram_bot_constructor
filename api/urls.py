# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'clients', views.ClientViewSet)

urlpatterns = [
    # Аутентификация
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),

    # Работа с компанией и пользователями
    path('company/<int:company_id>/', views.CompanyUpdateView.as_view(), name='update_company'),
    path('subusers/', views.SubUserListCreateView.as_view(), name='subuser_list_create'),

    # Данные по ботам и клиентам
    path('user_bots/', views.UserBotsView.as_view(), name='user_bots'),
    path('get_bot_username/', views.get_bot_username, name='get_bot_username'),

    # Импорт клиентов
    path('clients/import/', views.ClientImportView.as_view(), name='client_import'),
    path('clients/from_telegram/', views.TelegramClientDataView.as_view(), name='clients_from_telegram'),

    # DRF router
    path('', include(router.urls)),
]
