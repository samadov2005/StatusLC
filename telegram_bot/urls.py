from django.urls import path
from . import views

urlpatterns = [
    path('<str:token>/', views.webhook, name='telegram-webhook'),
]
