import logging
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.db.models import Q

from .models import (
    Attendance,
    Discount,
    Group,
    LearningCenter,
    Payment,
    PaymentStatus,
    Student,
    StudentStatus,
    Teacher,
    TeacherSalary,
)
from .serializers import (
    AttendanceSerializer,
    DiscountSerializer,
    GroupSerializer,
    LearningCenterSerializer,
    PaymentSerializer,
    StudentSerializer,
    TeacherSalarySerializer,
    TeacherSerializer,
)

logger = logging.getLogger(__name__)


def profile_role(user):
    profile = getattr(user, 'profile', None)
    return getattr(profile, 'role', None)


def is_operator_user(user):
    if not user or not user.is_authenticated:
        return False
    return user.is_staff or user.is_superuser or profile_role(user) in ('operator', 'admin')


def is_teacher_user(user):
    return bool(user and user.is_authenticated and hasattr(user, 'teacher_profile'))


class StaffWritePermission(BasePermission):
    """Allow authenticated reads, but only operators/admins can change data."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return is_operator_user(request.user)


class OperatorPermission(BasePermission):
    """Allow only operators/admins."""

    def has_permission(self, request, view):
        return is_operator_user(request.user)


class AttendancePermission(BasePermission):
    """Operators can manage all attendance; teachers can manage their own groups."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return is_operator_user(request.user) or is_teacher_user(request.user)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS or is_operator_user(request.user):
            return True
        teacher = getattr(request.user, 'teacher_profile', None)
        return bool(teacher and obj.group.teacher_id == teacher.id)


class TeacherViewSet(viewsets.ModelViewSet):
    """ViewSet for managing teachers."""
    queryset = Teacher.objects.all().select_related('user')
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated, OperatorPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['first_name', 'last_name', 'created_at']
    ordering = ['first_name']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class GroupViewSet(viewsets.ModelViewSet):
    """ViewSet for managing study groups."""
    queryset = Group.objects.all().select_related('teacher')
    serializer_class = GroupSerializer
    permission_classes = [StaffWritePermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'level', 'teacher__first_name', 'teacher__last_name']
    ordering_fields = ['name', 'level', 'day_of_week', 'start_time', 'created_at']
    ordering = ['day_of_week', 'start_time', 'name']
    
    def get_queryset(self):
        """Filter groups based on user role."""
        user = self.request.user
        if is_operator_user(user):
            return Group.objects.all().select_related('teacher').prefetch_related('schedules')
        
        # Teachers can only see their own groups
        if hasattr(user, 'teacher_profile'):
            return user.teacher_profile.groups.all().select_related('teacher').prefetch_related('schedules')
        
        return Group.objects.none()


class StudentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing students."""
    queryset = Student.objects.all().select_related('group', 'user')
    serializer_class = StudentSerializer
    permission_classes = [StaffWritePermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'phone', 'email', 'parent_phone']
    ordering_fields = ['first_name', 'last_name', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter students based on user role and access permissions."""
        user = self.request.user
        if is_operator_user(user):
            return Student.objects.all().select_related('group', 'user')
        
        # Teachers can see students in their groups
        if hasattr(user, 'teacher_profile'):
            return Student.objects.filter(group__teacher=user.teacher_profile).select_related('group', 'user')
        
        # Students can only see their own profile
        if hasattr(user, 'student_profile'):
            return Student.objects.filter(user=user).select_related('group', 'user')
        
        return Student.objects.none()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, OperatorPermission])
    def unpaid(self, request):
        """List students who have NOT paid for a given month.
        Provide `month` as YYYY-MM-DD (e.g., 2026-04-01) representing the month.
        """
        month = request.query_params.get('month')
        if not month:
            return Response(
                {'detail': 'Provide month parameter as YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            month_date = parse_date(month)
            if not month_date:
                raise ValueError("Invalid date format")
        except (ValueError, TypeError):
            return Response(
                {'detail': 'Invalid date format. Use YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        paid_student_ids = Payment.objects.filter(
            month=month_date,
            status=PaymentStatus.PAID
        ).values_list('student_id', flat=True)
        unpaid_students = Student.objects.filter(
            status=StudentStatus.ACTIVE
        ).exclude(id__in=paid_student_ids).select_related('group', 'user')
        
        page = self.paginate_queryset(unpaid_students)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(unpaid_students, many=True)
        return Response(serializer.data)


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing student payments."""
    queryset = Payment.objects.all().select_related('student', 'group', 'created_by')
    serializer_class = PaymentSerializer
    permission_classes = [StaffWritePermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__first_name', 'student__last_name', 'reference_number', 'notes']
    ordering_fields = ['month', 'paid_at', 'amount']
    ordering = ['-month']
    
    def get_queryset(self):
        """Filter payments based on user role."""
        user = self.request.user
        if is_operator_user(user):
            return Payment.objects.all().select_related('student', 'group', 'created_by')
        
        # Teachers can see payments for students in their groups
        if hasattr(user, 'teacher_profile'):
            return Payment.objects.filter(student__group__teacher=user.teacher_profile).select_related('student', 'group')
        
        # Students can only see their own payments
        if hasattr(user, 'student_profile'):
            return Payment.objects.filter(student=user.student_profile).select_related('student', 'group')
        
        return Payment.objects.none()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AttendanceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing attendance records."""
    queryset = Attendance.objects.all().select_related('student', 'group', 'recorded_by')
    serializer_class = AttendanceSerializer
    permission_classes = [AttendancePermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__first_name', 'student__last_name', 'group__name', 'note']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']
    
    def get_queryset(self):
        """Filter and search attendance records."""
        qs = Attendance.objects.all().select_related('student', 'group', 'recorded_by')
        user = self.request.user
        
        # Permission-based filtering
        if not is_operator_user(user):
            # Teachers can see attendance for their groups
            if hasattr(user, 'teacher_profile'):
                qs = qs.filter(group__teacher=user.teacher_profile)
            # Students can see their own attendance
            elif hasattr(user, 'student_profile'):
                qs = qs.filter(student=user.student_profile)
            else:
                qs = qs.none()
        
        # Apply query parameter filters
        group_id = self.request.query_params.get('group')
        date = self.request.query_params.get('date')
        student_id = self.request.query_params.get('student')
        
        if group_id:
            qs = qs.filter(group_id=group_id)
        if date:
            qs = qs.filter(date=date)
        if student_id:
            qs = qs.filter(student_id=student_id)
        
        return qs

    def perform_create(self, serializer):
        group = serializer.validated_data.get('group')
        if not is_operator_user(self.request.user):
            teacher = getattr(self.request.user, 'teacher_profile', None)
            if not teacher or not group or group.teacher_id != teacher.id:
                raise PermissionDenied("You can record attendance only for your own groups.")
        serializer.save(recorded_by=self.request.user)

    def perform_update(self, serializer):
        group = serializer.validated_data.get('group', serializer.instance.group)
        if not is_operator_user(self.request.user):
            teacher = getattr(self.request.user, 'teacher_profile', None)
            if not teacher or not group or group.teacher_id != teacher.id:
                raise PermissionDenied("You can update attendance only for your own groups.")
        serializer.save()


class DiscountViewSet(viewsets.ModelViewSet):
    """ViewSet for managing discounts."""
    queryset = Discount.objects.all().prefetch_related('applicable_groups', 'applicable_students')
    serializer_class = DiscountSerializer
    permission_classes = [IsAuthenticated, OperatorPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'start_date', 'created_at']
    ordering = ['-created_at']


class TeacherSalaryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing teacher salaries."""
    queryset = TeacherSalary.objects.all().select_related('teacher')
    serializer_class = TeacherSalarySerializer
    permission_classes = [IsAuthenticated, OperatorPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['teacher__first_name', 'teacher__last_name']
    ordering_fields = ['month', 'total_salary', 'created_at']
    ordering = ['-month']


class LearningCenterViewSet(viewsets.ModelViewSet):
    """ViewSet for managing learning center settings."""
    queryset = LearningCenter.objects.all()
    serializer_class = LearningCenterSerializer
    permission_classes = [IsAuthenticated, OperatorPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'email', 'phone', 'address']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


@api_view(['GET'])
@permission_classes([AllowAny])
def public_overview(request):
    """Public learning center overview for guest visitors."""
    current_month = timezone.localdate().replace(day=1)
    center = LearningCenter.objects.first()
    groups = Group.objects.filter(is_active=True).select_related('teacher').prefetch_related('schedules', 'students')
    payload_groups = []

    for group in groups:
        paid_ids = set(
            Payment.objects.filter(group=group, month=current_month, status=PaymentStatus.PAID)
            .values_list('student_id', flat=True)
        )
        latest_attendance = {}
        for row in Attendance.objects.filter(group=group).select_related('student').order_by('-date'):
            latest_attendance.setdefault(row.student_id, row)
        students = []
        for student in group.students.filter(status=StudentStatus.ACTIVE):
            attendance = latest_attendance.get(student.id)
            students.append({
                'id': student.id,
                'full_name': student.full_name,
                'payment_paid': student.id in paid_ids,
                'payment_status': "To'langan" if student.id in paid_ids else 'Kutilmoqda',
                'payment_month': current_month.isoformat(),
                'attendance_status': attendance.get_status_display() if attendance else 'Yozuv yo\'q',
                'attendance_date': attendance.date.isoformat() if attendance else '',
                'homework_status': attendance.homework_status if attendance else 'not_checked',
                'homework_status_display': attendance.get_homework_status_display() if attendance else 'Tekshirilmagan',
            })

        present_count = sum(1 for student in students if student['attendance_status'] in ('Kelgan', 'Kechikkan'))
        homework_done_count = sum(1 for student in students if student['homework_status'] == 'done')

        payload_groups.append({
            'id': group.id,
            'name': group.name,
            'level': group.level,
            'teacher_name': group.teacher.full_name if group.teacher else '',
            'schedule_display': GroupSerializer(group).data['schedule_display'],
            'tuition_fee': str(group.tuition_fee),
            'students_count': len(students),
            'paid_students_count': len(paid_ids),
            'present_students_count': present_count,
            'homework_done_count': homework_done_count,
            'students': students,
        })

    return Response({
        'center': LearningCenterSerializer(center).data if center else None,
        'current_month': current_month.isoformat(),
        'groups': payload_groups,
    })

