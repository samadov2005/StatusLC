from rest_framework import routers
from django.urls import path, include
from .views import (
    AttendanceViewSet,
    DiscountViewSet,
    GroupViewSet,
    LearningCenterViewSet,
    PaymentViewSet,
    StudentViewSet,
    TeacherSalaryViewSet,
    TeacherViewSet,
    public_overview,
)

router = routers.DefaultRouter()
router.register(r'teachers', TeacherViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'students', StudentViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'attendances', AttendanceViewSet)
router.register(r'discounts', DiscountViewSet)
router.register(r'teacher-salaries', TeacherSalaryViewSet)
router.register(r'learning-centers', LearningCenterViewSet)

urlpatterns = [
    path('public/', public_overview, name='public-overview'),
    path('', include(router.urls)),
]
