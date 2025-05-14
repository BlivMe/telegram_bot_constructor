# backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from bots import views as bots_views
from api import views as api_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/bots/', include('bots.urls')),
    path('api/core/', include('api.urls')),
    path('', bots_views.index, name='home'),
    path('api/core/user_bots/', api_views.UserBotsView.as_view(), name='user_bots'),
]
