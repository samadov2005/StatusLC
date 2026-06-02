from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.authtoken.views import obtain_auth_token
from accounts import views as account_views
from accounts import api_views as account_api_views
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/session/', account_views.operator_session, name='operator-session'),
    path('api/auth/login/', account_views.operator_login, name='operator-login'),
    path('api/auth/logout/', account_views.operator_logout, name='operator-logout'),
    path('api/auth/token/', obtain_auth_token, name='api-token-auth'),
    path('api/auth/me/', account_api_views.OperatorMe.as_view(), name='api-token-me'),
    path('api/', include('core.urls')),
    path('health/', core_views.health, name='health'),
    path('telegram/', include('telegram_bot.urls')),
    # Serve frontend SPA built at /student/dashboard/
    path('student/dashboard/', TemplateView.as_view(template_name='student_dashboard/index.html'), name='student-dashboard'),
    path('', include('accounts.urls')),
]
