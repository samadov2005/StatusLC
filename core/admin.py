from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Teacher, Group, GroupSchedule, Student, Payment, Attendance,
    Discount, TeacherSalary, LearningCenter,
    TeacherStatus, StudentStatus, PaymentStatus, AttendanceStatus
)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'status_colored', 'get_active_groups_count', 'hire_date')
    list_filter = ('status', 'hire_date', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'get_total_students', 'get_active_groups_count')
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'address')
        }),
        ('Employment', {
            'fields': ('status', 'hire_date', 'hourly_rate')
        }),
        ('User Account', {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('get_active_groups_count', 'get_total_students'),
            'classes': ('collapse',)
        }),
        ('Audit Trail', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'hire_date'

    def status_colored(self, obj):
        colors = {
            TeacherStatus.ACTIVE: 'green',
            TeacherStatus.INACTIVE: 'gray',
            TeacherStatus.LEAVE: 'orange',
            TeacherStatus.TERMINATED: 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = 'Status'


class GroupScheduleInline(admin.TabularInline):
    model = GroupSchedule
    extra = 1


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    inlines = (GroupScheduleInline,)
    list_display = ('name', 'level', 'get_schedule', 'teacher', 'student_count', 'available_seats', 'tuition_fee')
    list_filter = ('level', 'is_active', 'day_of_week', 'created_at')
    search_fields = ('name', 'level', 'teacher__first_name', 'teacher__last_name')
    readonly_fields = ('created_at', 'updated_at', 'student_count', 'available_seats', 'class_duration_hours')
    fieldsets = (
        ('Group Information', {
            'fields': ('name', 'description', 'level')
        }),
        ('Schedule', {
            'fields': ('day_of_week', 'start_time', 'end_time', 'class_duration_hours')
        }),
        ('Capacity', {
            'fields': ('max_students', 'min_students', 'student_count', 'available_seats')
        }),
        ('Teacher', {
            'fields': ('teacher',)
        }),
        ('Tuition', {
            'fields': ('tuition_fee',)
        }),
        ('Status', {
            'fields': ('is_active', 'start_date', 'end_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_schedule(self, obj):
        schedules = list(obj.schedules.all())
        if schedules:
            return ', '.join(
                f"{schedule.get_day_of_week_display()} {schedule.start_time.strftime('%H:%M')}-{schedule.end_time.strftime('%H:%M')}"
                for schedule in schedules
            )
        day = obj.get_day_of_week_display() if obj.day_of_week else ''
        return f"{day} {obj.start_time.strftime('%H:%M')}-{obj.end_time.strftime('%H:%M')}".strip()
    get_schedule.short_description = 'Schedule'


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'group', 'status_colored', 'enrollment_date', 'user')
    list_filter = ('group', 'status', 'enrollment_date')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'parent_phone')
    readonly_fields = ('created_at', 'updated_at', 'age')
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'age')
        }),
        ('Parent/Guardian', {
            'fields': ('parent_name', 'parent_phone', 'parent_email'),
            'classes': ('collapse',)
        }),
        ('Enrollment', {
            'fields': ('group', 'status', 'enrollment_date')
        }),
        ('Account', {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'enrollment_date'
    
    def status_colored(self, obj):
        colors = {
            StudentStatus.ACTIVE: 'green',
            StudentStatus.INACTIVE: 'gray',
            StudentStatus.GRADUATED: 'blue',
            StudentStatus.SUSPENDED: 'orange',
            StudentStatus.DROPPED: 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = 'Status'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'group', 'month', 'amount', 'status_colored', 'payment_method', 'confirmed_at')
    list_filter = ('status', 'month', 'payment_method', 'confirmed_at')
    search_fields = ('student__first_name', 'student__last_name', 'reference_number')
    readonly_fields = ('paid_at', 'is_overdue')
    fieldsets = (
        ('Payment Information', {
            'fields': ('student', 'group', 'month', 'amount')
        }),
        ('Payment Details', {
            'fields': ('status', 'payment_method', 'reference_number')
        }),
        ('Timestamps', {
            'fields': ('paid_at', 'confirmed_at', 'is_overdue')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_by',),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'month'
    
    def status_colored(self, obj):
        colors = {
            PaymentStatus.PAID: 'green',
            PaymentStatus.PENDING: 'orange',
            PaymentStatus.OVERDUE: 'red',
            PaymentStatus.PARTIAL: 'blue',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = 'Status'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'group', 'date', 'status_colored', 'minutes_present', 'recorded_by')
    list_filter = ('status', 'date', 'group', 'created_at')
    search_fields = ('student__first_name', 'student__last_name', 'group__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Attendance Information', {
            'fields': ('student', 'group', 'date', 'status')
        }),
        ('Duration', {
            'fields': ('minutes_present',)
        }),
        ('Notes', {
            'fields': ('note',),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('recorded_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'date'

    def status_colored(self, obj):
        colors = {
            AttendanceStatus.PRESENT: 'green',
            AttendanceStatus.ABSENT: 'red',
            AttendanceStatus.LATE: 'orange',
            AttendanceStatus.EXCUSED: 'blue',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = 'Status'


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount_type', 'value', 'is_active', 'start_date', 'end_date')
    list_filter = ('discount_type', 'is_active', 'start_date')
    search_fields = ('name', 'description')
    filter_horizontal = ('applicable_groups', 'applicable_students')
    fieldsets = (
        ('Discount Information', {
            'fields': ('name', 'description', 'discount_type', 'value')
        }),
        ('Applicability', {
            'fields': ('applicable_groups', 'applicable_students')
        }),
        ('Validity', {
            'fields': ('is_active', 'start_date', 'end_date')
        }),
    )


@admin.register(TeacherSalary)
class TeacherSalaryAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'month', 'teaching_hours', 'total_salary', 'is_paid', 'paid_at')
    list_filter = ('is_paid', 'month', 'teacher')
    search_fields = ('teacher__first_name', 'teacher__last_name')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Teacher & Month', {
            'fields': ('teacher', 'month')
        }),
        ('Calculation', {
            'fields': ('teaching_hours', 'hourly_rate', 'bonus', 'deductions', 'total_salary')
        }),
        ('Payment Status', {
            'fields': ('is_paid', 'paid_at')
        }),
        ('Audit', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'month'


@admin.register(LearningCenter)
class LearningCenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'currency', 'default_tuition_fee')
    fieldsets = (
        ('Organization Information', {
            'fields': ('name', 'description', 'address')
        }),
        ('Contact', {
            'fields': ('email', 'phone')
        }),
        ('Financial Settings', {
            'fields': ('currency', 'default_tuition_fee')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
