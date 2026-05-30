from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.student_signup, name='student-signup'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('api/auth/session/', views.operator_session, name='operator-session'),
    path('api/auth/login/', views.operator_login, name='operator-login'),
    path('api/auth/logout/', views.operator_logout, name='operator-logout'),
    path('student/dashboard/', views.student_dashboard, name='student-dashboard'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher-dashboard'),
]
