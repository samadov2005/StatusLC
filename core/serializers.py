from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import (
    Attendance,
    AttendanceStatus,
    Discount,
    Group,
    GroupSchedule,
    LearningCenter,
    Payment,
    PaymentStatus,
    Student,
    Teacher,
    TeacherSalary,
)


class GroupScheduleSerializer(serializers.ModelSerializer):
    """Serializer for group class days and times."""
    day_display = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = GroupSchedule
        fields = ('id', 'day_of_week', 'day_display', 'start_time', 'end_time')

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({'end_time': "End time must be after start time."})
        return attrs


class TeacherSerializer(serializers.ModelSerializer):
    """Serializer for Teacher model."""
    groups_count = serializers.SerializerMethodField()
    assigned_groups = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        many=True,
        required=False,
        source='groups',
    )
    full_name = serializers.CharField(read_only=True)
    username = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, min_length=8)

    class Meta:
        model = Teacher
        fields = (
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'status', 'hourly_rate', 'hire_date', 'user', 'groups_count',
            'assigned_groups', 'username', 'password', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at', 'user')

    def get_groups_count(self, obj):
        return obj.groups.count()

    def validate_hire_date(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError("Hire date cannot be in the future.")
        return value

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        username = attrs.get('username', '')
        password = attrs.get('password', '')

        if instance is None and not (username and password):
            raise serializers.ValidationError({'username': "Username and password are both required to create a teacher account."})
        if username and get_user_model().objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': "This username is already taken."})
        return attrs

    def create(self, validated_data):
        username = validated_data.pop('username', '')
        password = validated_data.pop('password', '')
        assigned_groups = validated_data.pop('groups', [])
        teacher = super().create(validated_data)
        if assigned_groups:
            Group.objects.filter(id__in=[group.id for group in assigned_groups]).update(teacher=teacher)

        if username and password:
            user = get_user_model().objects.create_user(
                username=username,
                password=password,
                first_name=teacher.first_name,
                last_name=teacher.last_name,
                email=teacher.email,
            )
            user.profile.role = 'teacher'
            user.profile.phone = teacher.phone
            user.profile.save()
            teacher.user = user
            teacher.save(update_fields=['user'])
        return teacher

    def update(self, instance, validated_data):
        username = validated_data.pop('username', '')
        password = validated_data.pop('password', '')
        assigned_groups = validated_data.pop('groups', None)
        teacher = super().update(instance, validated_data)
        if assigned_groups is not None:
            Group.objects.filter(teacher=teacher).exclude(id__in=[group.id for group in assigned_groups]).update(teacher=None)
            Group.objects.filter(id__in=[group.id for group in assigned_groups]).update(teacher=teacher)

        if teacher.user:
            teacher.user.first_name = teacher.first_name
            teacher.user.last_name = teacher.last_name
            teacher.user.email = teacher.email
            if password:
                teacher.user.set_password(password)
            teacher.user.save()
            teacher.user.profile.role = 'teacher'
            teacher.user.profile.phone = teacher.phone
            teacher.user.profile.save()
        elif username and password:
            user = get_user_model().objects.create_user(
                username=username,
                password=password,
                first_name=teacher.first_name,
                last_name=teacher.last_name,
                email=teacher.email,
            )
            user.profile.role = 'teacher'
            user.profile.phone = teacher.phone
            user.profile.save()
            teacher.user = user
            teacher.save(update_fields=['user'])
        return teacher


class GroupSerializer(serializers.ModelSerializer):
    """Serializer for Group model."""
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    schedules = GroupScheduleSerializer(many=True, required=False)
    students_count = serializers.SerializerMethodField()
    paid_students_count = serializers.SerializerMethodField()
    unpaid_students_count = serializers.SerializerMethodField()
    available_seats = serializers.IntegerField(read_only=True)
    schedule_display = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = (
            'id', 'name', 'description', 'level', 'day_of_week',
            'start_time', 'end_time', 'schedules', 'schedule_display', 'max_students',
            'min_students', 'available_seats', 'teacher', 'teacher_name',
            'is_active', 'start_date', 'end_date', 'tuition_fee',
            'students_count', 'paid_students_count', 'unpaid_students_count',
            'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')

    def get_students_count(self, obj):
        return obj.students.count()

    def get_paid_students_count(self, obj):
        month = timezone.localdate().replace(day=1)
        return obj.payments.filter(month=month, status=PaymentStatus.PAID).values('student_id').distinct().count()

    def get_unpaid_students_count(self, obj):
        return max(0, self.get_students_count(obj) - self.get_paid_students_count(obj))

    def get_schedule_display(self, obj):
        schedules = list(obj.schedules.all()) if getattr(obj, 'pk', None) else []
        if schedules:
            return ', '.join(
                f"{schedule.get_day_of_week_display()} {schedule.start_time:%H:%M}-{schedule.end_time:%H:%M}"
                for schedule in schedules
            )
        day = obj.get_day_of_week_display() if obj.day_of_week else ''
        time_range = f"{obj.start_time:%H:%M}-{obj.end_time:%H:%M}"
        return f"{day} {time_range}".strip()

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        start_time = attrs.get('start_time', getattr(instance, 'start_time', None))
        end_time = attrs.get('end_time', getattr(instance, 'end_time', None))
        min_students = attrs.get('min_students', getattr(instance, 'min_students', None))
        max_students = attrs.get('max_students', getattr(instance, 'max_students', None))
        start_date = attrs.get('start_date', getattr(instance, 'start_date', None))
        end_date = attrs.get('end_date', getattr(instance, 'end_date', None))

        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({'end_time': "End time must be after start time."})
        if min_students and max_students and min_students > max_students:
            raise serializers.ValidationError({'min_students': "Minimum students cannot exceed maximum students."})
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({'end_date': "End date cannot be before start date."})
        return attrs

    def create(self, validated_data):
        schedules_data = validated_data.pop('schedules', [])
        group = super().create(validated_data)
        self._replace_schedules(group, schedules_data)
        return group

    def update(self, instance, validated_data):
        schedules_data = validated_data.pop('schedules', None)
        group = super().update(instance, validated_data)
        if schedules_data is not None:
            self._replace_schedules(group, schedules_data)
        return group

    def _replace_schedules(self, group, schedules_data):
        if not schedules_data:
            return
        group.schedules.all().delete()
        GroupSchedule.objects.bulk_create([
            GroupSchedule(group=group, **schedule)
            for schedule in schedules_data
        ])


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for Student model."""
    group_name = serializers.SerializerMethodField()
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)

    class Meta:
        model = Student
        fields = (
            'id', 'full_name', 'first_name', 'last_name', 'email', 'phone',
            'date_of_birth', 'age', 'parent_name', 'parent_phone',
            'parent_email', 'group', 'group_name', 'status',
            'enrollment_date', 'user', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')

    def get_group_name(self, obj):
        return str(obj.group) if obj.group else ''

    def validate_date_of_birth(self, value):
        if value and value > timezone.localdate():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    group_name = serializers.SerializerMethodField()
    month_display = serializers.DateField(source='month', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Payment
        fields = (
            'id', 'student', 'student_name', 'group', 'group_name',
            'amount', 'month', 'month_display', 'status', 'payment_method',
            'reference_number', 'confirmed_at', 'is_overdue', 'notes', 'paid_at'
        )
        read_only_fields = ('paid_at',)

    def get_group_name(self, obj):
        return str(obj.group) if obj.group else ''

    def validate_month(self, value):
        if value.day != 1:
            raise serializers.ValidationError("Payment month must be the first day of the month.")
        return value

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        student = attrs.get('student', getattr(instance, 'student', None))
        group = attrs.get('group', getattr(instance, 'group', None))

        if student and group and student.group_id and student.group_id != group.id:
            raise serializers.ValidationError({'group': "Payment group must match the student's assigned group."})
        return attrs


class AttendanceSerializer(serializers.ModelSerializer):
    """Serializer for Attendance model."""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    group_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    homework_status_display = serializers.CharField(source='get_homework_status_display', read_only=True)
    is_present = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = (
            'id', 'student', 'student_name', 'group', 'group_name', 'date',
            'status', 'status_display', 'is_present', 'minutes_present',
            'note', 'homework_status', 'homework_status_display',
            'homework_note', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')

    def get_is_present(self, obj):
        return obj.status in (AttendanceStatus.PRESENT, AttendanceStatus.LATE)

    def get_group_name(self, obj):
        return str(obj.group) if obj.group else ''

    def validate_date(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError("Attendance date cannot be in the future.")
        return value

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        student = attrs.get('student', getattr(instance, 'student', None))
        group = attrs.get('group', getattr(instance, 'group', None))

        if student and group and student.group_id and student.group_id != group.id:
            raise serializers.ValidationError({'group': "Attendance group must match the student's assigned group."})
        return attrs


class DiscountSerializer(serializers.ModelSerializer):
    """Serializer for discount rules."""

    class Meta:
        model = Discount
        fields = (
            'id', 'name', 'description', 'discount_type', 'value',
            'applicable_groups', 'applicable_students', 'start_date',
            'end_date', 'is_active', 'created_at'
        )
        read_only_fields = ('created_at',)

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        discount_type = attrs.get('discount_type', getattr(instance, 'discount_type', None))
        value = attrs.get('value', getattr(instance, 'value', None))
        start_date = attrs.get('start_date', getattr(instance, 'start_date', None))
        end_date = attrs.get('end_date', getattr(instance, 'end_date', None))

        if discount_type == 'percentage' and value is not None and value > 100:
            raise serializers.ValidationError({'value': "Percentage discount cannot exceed 100."})
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({'end_date': "End date cannot be before start date."})
        return attrs


class TeacherSalarySerializer(serializers.ModelSerializer):
    """Serializer for teacher salaries."""
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)

    class Meta:
        model = TeacherSalary
        fields = (
            'id', 'teacher', 'teacher_name', 'month', 'teaching_hours',
            'hourly_rate', 'bonus', 'deductions', 'total_salary',
            'is_paid', 'paid_at', 'created_at'
        )
        read_only_fields = ('created_at',)
        extra_kwargs = {
            'total_salary': {'required': False},
        }

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        month = attrs.get('month', getattr(instance, 'month', None))
        teaching_hours = attrs.get('teaching_hours', getattr(instance, 'teaching_hours', 0))
        hourly_rate = attrs.get('hourly_rate', getattr(instance, 'hourly_rate', 0))
        bonus = attrs.get('bonus', getattr(instance, 'bonus', 0))
        deductions = attrs.get('deductions', getattr(instance, 'deductions', 0))

        if month and month.day != 1:
            raise serializers.ValidationError({'month': "Salary month must be the first day of the month."})
        calculated_total = teaching_hours * hourly_rate + bonus - deductions
        if calculated_total < 0:
            raise serializers.ValidationError({'total_salary': "Salary total cannot be negative."})
        attrs['total_salary'] = calculated_total
        return attrs


class LearningCenterSerializer(serializers.ModelSerializer):
    """Serializer for learning center settings."""

    class Meta:
        model = LearningCenter
        fields = (
            'id', 'name', 'description', 'email', 'phone', 'address',
            'currency', 'default_tuition_fee', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')

