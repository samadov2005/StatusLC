from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


# ==================== ENUMS & CHOICES ====================
class TeacherStatus(models.TextChoices):
    """Teacher employment status"""
    ACTIVE = 'active', 'Faol'
    INACTIVE = 'inactive', 'Nofaol'
    LEAVE = 'leave', "Ta'tilda"
    TERMINATED = 'terminated', "Ishdan bo'shatilgan"


class StudentStatus(models.TextChoices):
    """Student enrollment status"""
    ACTIVE = 'active', 'Faol'
    INACTIVE = 'inactive', 'Nofaol'
    GRADUATED = 'graduated', 'Bitirgan'
    SUSPENDED = 'suspended', "To'xtatilgan"
    DROPPED = 'dropped', 'Ketgan'


class PaymentStatus(models.TextChoices):
    """Payment status"""
    PAID = 'paid', "To'langan"
    PENDING = 'pending', 'Kutilmoqda'
    OVERDUE = 'overdue', "Muddati o'tgan"
    PARTIAL = 'partial', 'Qisman'


class AttendanceStatus(models.TextChoices):
    """Attendance status"""
    PRESENT = 'present', 'Kelgan'
    ABSENT = 'absent', 'Kelmagan'
    LATE = 'late', 'Kechikkan'
    EXCUSED = 'excused', 'Uzrli'


class HomeworkStatus(models.TextChoices):
    """Homework completion status for a class."""
    NOT_CHECKED = 'not_checked', 'Tekshirilmagan'
    DONE = 'done', 'Bajargan'
    PARTIAL = 'partial', 'Qisman'
    NOT_DONE = 'not_done', 'Bajarmagan'


# ==================== CORE MODELS ====================
class Teacher(models.Model):
    """Represents a teacher in the learning center."""
    first_name = models.CharField(max_length=100, help_text="Teacher's first name")
    last_name = models.CharField(max_length=100, blank=True, help_text="Teacher's last name")
    email = models.EmailField(unique=True, help_text="Teacher's email address")
    phone = models.CharField(max_length=30, help_text="Phone number for contact")
    address = models.TextField(blank=True, help_text="Physical address")
    
    # Employment info
    status = models.CharField(
        max_length=20, 
        choices=TeacherStatus.choices, 
        default=TeacherStatus.ACTIVE,
        help_text="Employment status"
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Hourly rate in local currency"
    )
    hire_date = models.DateField(help_text="Date hired")
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='teacher_profile',
        help_text="Associated user account"
    )
    
    # Audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_teachers',
        help_text="User who created this record"
    )

    class Meta:
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'
        indexes = [
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['status']),
            models.Index(fields=['email']),
        ]
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_active_groups_count(self):
        """Count active groups taught by this teacher"""
        return self.groups.filter(is_active=True).count()
    
    def get_total_students(self):
        """Total students in all groups"""
        return Student.objects.filter(group__teacher=self, status=StudentStatus.ACTIVE).count()


class Group(models.Model):
    """Represents a study group with a specific schedule and teacher."""
    name = models.CharField(max_length=200, help_text="Group name (e.g., 'English A1')")
    description = models.TextField(blank=True, help_text="Group description and objectives")
    level = models.CharField(max_length=100, help_text="Proficiency level (A1, A2, B1, etc.)")
    
    # Schedule
    day_of_week = models.CharField(
        max_length=20,
        choices=[
            ('monday', 'Dushanba (Monday)'),
            ('tuesday', 'Seshanba (Tuesday)'),
            ('wednesday', 'Chorshanba (Wednesday)'),
            ('thursday', 'Payshanba (Thursday)'),
            ('friday', 'Juma (Friday)'),
            ('saturday', 'Shanba (Saturday)'),
            ('sunday', 'Yakshanba (Sunday)'),
        ],
        blank=True,
        help_text="Day of week for classes"
    )
    start_time = models.TimeField(help_text="Class start time (e.g., 18:00)")
    end_time = models.TimeField(help_text="Class end time (e.g., 19:30)")
    
    # Capacity
    max_students = models.IntegerField(
        default=20,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Maximum number of students"
    )
    min_students = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1)],
        help_text="Minimum students to keep group active"
    )
    
    # Teacher
    teacher = models.ForeignKey(
        Teacher,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='groups',
        help_text="Assigned teacher"
    )
    
    # Status
    is_active = models.BooleanField(default=True, help_text="Is the group currently active?")
    start_date = models.DateField(default=timezone.localdate, help_text="Group start date")
    end_date = models.DateField(null=True, blank=True, help_text="Group end date (if completed)")
    
    # Tuition fee for this group
    tuition_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Monthly tuition fee per student"
    )
    
    # Audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'
        ordering = ['name']
        indexes = [
            models.Index(fields=['teacher']),
            models.Index(fields=['level']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.level})"
    
    @property
    def student_count(self):
        """Current number of active students"""
        return self.students.filter(status=StudentStatus.ACTIVE).count()
    
    @property
    def available_seats(self):
        """Number of available seats"""
        return max(0, self.max_students - self.student_count)
    
    @property
    def class_duration_hours(self):
        """Duration of class in hours"""
        from datetime import datetime
        start = datetime.combine(timezone.now().date(), self.start_time)
        end = datetime.combine(timezone.now().date(), self.end_time)
        return (end - start).total_seconds() / 3600


class GroupSchedule(models.Model):
    """A class day/time slot for a group."""
    DAY_CHOICES = [
        ('monday', 'Dushanba'),
        ('tuesday', 'Seshanba'),
        ('wednesday', 'Chorshanba'),
        ('thursday', 'Payshanba'),
        ('friday', 'Juma'),
        ('saturday', 'Shanba'),
        ('sunday', 'Yakshanba'),
    ]

    group = models.ForeignKey(
        Group,
        related_name='schedules',
        on_delete=models.CASCADE,
        help_text='Group schedule owner'
    )
    day_of_week = models.CharField(max_length=20, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ('group', 'day_of_week', 'start_time')
        indexes = [
            models.Index(fields=['group', 'day_of_week']),
        ]

    def __str__(self):
        return f"{self.group} - {self.get_day_of_week_display()} {self.start_time:%H:%M}-{self.end_time:%H:%M}"


class Student(models.Model):
    """Represents a student enrolled in the learning center."""
    # Personal info
    first_name = models.CharField(max_length=100, help_text="Student's first name")
    last_name = models.CharField(max_length=100, blank=True, help_text="Student's last name")
    email = models.EmailField(blank=True, help_text="Student's email address")
    phone = models.CharField(max_length=30, help_text="Student's phone number")
    date_of_birth = models.DateField(null=True, blank=True, help_text="Student's date of birth")
    
    # Parent/Guardian contact
    parent_name = models.CharField(max_length=200, blank=True, help_text="Parent/Guardian name")
    parent_phone = models.CharField(max_length=30, blank=True, help_text="Parent/Guardian phone number")
    parent_email = models.EmailField(blank=True, help_text="Parent/Guardian email")
    
    # Enrollment
    group = models.ForeignKey(
        Group,
        related_name='students',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Enrolled study group"
    )
    status = models.CharField(
        max_length=20,
        choices=StudentStatus.choices,
        default=StudentStatus.ACTIVE,
        help_text="Enrollment status"
    )
    enrollment_date = models.DateField(
        default=timezone.localdate,
        help_text="Date student enrolled"
    )
    
    # User account
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='student_profile',
        help_text="Associated user account"
    )
    
    # Audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['group']),
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['phone']),
        ]

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or f"Student {self.id}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def age(self):
        """Calculate age from date of birth"""
        if not self.date_of_birth:
            return None
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def is_paid_for_month(self, month_date):
        """Check if student has paid for the given month."""
        from datetime import date
        if isinstance(month_date, str):
            month_date = date.fromisoformat(month_date)
        return self.payments.filter(
            month__year=month_date.year,
            month__month=month_date.month,
            status=PaymentStatus.PAID
        ).exists()
    
    def get_unpaid_months(self, limit_months=3):
        """Get recent unpaid months"""
        from datetime import timedelta, date
        unpaid = []
        today = timezone.now().date()
        
        for i in range(limit_months):
            check_date = (today - timedelta(days=30*i)).replace(day=1)
            if not self.is_paid_for_month(check_date):
                unpaid.append(check_date)
        
        return unpaid
    
    def get_total_paid(self, year=None):
        """Get total amount paid in a year or current year"""
        if year is None:
            year = timezone.now().year
        return self.payments.filter(
            month__year=year,
            status=PaymentStatus.PAID
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0



class Payment(models.Model):
    """Records student payments for monthly tuition."""
    student = models.ForeignKey(
        Student,
        related_name='payments',
        on_delete=models.CASCADE,
        help_text="Student who made the payment"
    )
    group = models.ForeignKey(
        Group,
        related_name='payments',
        null=True,
        on_delete=models.SET_NULL,
        help_text="Group for which payment is made"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Payment amount in local currency"
    )
    month = models.DateField(help_text='Month for payment (use 1st day of month)')
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        help_text="Payment status"
    )
    
    # Payment details
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('cash', 'Naqd (Cash)'),
            ('card', 'Karta (Card)'),
            ('transfer', 'O\'tkazma (Transfer)'),
            ('mobile', 'Mobil (Mobile)'),
            ('other', 'Boshqa (Other)'),
        ],
        default='cash',
        help_text="Payment method"
    )
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Transaction/receipt reference number"
    )
    
    # Timestamps
    paid_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True, help_text="When payment was confirmed")
    
    # Notes
    notes = models.TextField(blank=True, help_text="Additional payment notes")
    
    # Audit trail
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_payments',
        help_text="User who recorded the payment"
    )

    class Meta:
        unique_together = ('student', 'group', 'month')
        ordering = ['-month', '-paid_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        indexes = [
            models.Index(fields=['student', 'month']),
            models.Index(fields=['month']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.student} - {self.month.strftime('%Y-%m')}: {self.amount}"
    
    @property
    def is_overdue(self):
        """Check if payment is overdue"""
        if self.status == PaymentStatus.PAID:
            return False
        from datetime import date, datetime, timedelta
        # Payment is overdue if month is more than 30 days in the past
        today = date.today()
        return self.month < (today - timedelta(days=30))
    
    def mark_as_paid(self, confirmed_at=None):
        """Mark payment as paid"""
        self.status = PaymentStatus.PAID
        self.confirmed_at = confirmed_at or timezone.now()
        self.save()


class Discount(models.Model):
    """Discount management for students or groups"""
    DISCOUNT_TYPES = [
        ('percentage', 'Foiz'),
        ('fixed', "So'm"),
    ]
    
    name = models.CharField(max_length=200, help_text="Discount name")
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=50, choices=DISCOUNT_TYPES)
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Discount value (% or amount)"
    )
    
    # Applicability
    applicable_groups = models.ManyToManyField(
        Group,
        blank=True,
        help_text="Groups where discount applies (leave empty for all)"
    )
    applicable_students = models.ManyToManyField(
        Student,
        blank=True,
        help_text="Students who get this discount (leave empty for all)"
    )
    
    # Validity
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        suffix = '%' if self.discount_type == 'percentage' else " so'm"
        return f"{self.name} ({self.value}{suffix})"
    
    def is_valid(self):
        """Check if discount is valid for today"""
        today = timezone.now().date()
        return (
            self.is_active and
            self.start_date <= today and
            (self.end_date is None or today <= self.end_date)
        )
    
    def calculate_discount_amount(self, amount):
        """Calculate discount amount"""
        if self.discount_type == 'percentage':
            return amount * self.value / 100
        return min(self.value, amount)



class Attendance(models.Model):
    """Records student attendance for each class."""
    student = models.ForeignKey(
        Student,
        related_name='attendances',
        on_delete=models.CASCADE,
        help_text="Student attendance"
    )
    group = models.ForeignKey(
        Group,
        related_name='attendances',
        on_delete=models.CASCADE,
        help_text="Group for this attendance record"
    )
    date = models.DateField(help_text="Class date")
    status = models.CharField(
        max_length=20,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT,
        help_text="Attendance status"
    )
    note = models.CharField(
        max_length=200,
        blank=True,
        help_text="Reason for absence or late arrival"
    )
    homework_status = models.CharField(
        max_length=20,
        choices=HomeworkStatus.choices,
        default=HomeworkStatus.NOT_CHECKED,
        help_text="Student homework completion status"
    )
    homework_note = models.CharField(
        max_length=200,
        blank=True,
        help_text="Homework note or teacher comment"
    )
    
    # Duration/completion
    minutes_present = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Minutes present in class (0 if not tracked)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='recorded_attendances',
        help_text="User who recorded attendance"
    )

    class Meta:
        unique_together = ('student', 'group', 'date')
        ordering = ['-date']
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'
        indexes = [
            models.Index(fields=['group', 'date']),
            models.Index(fields=['student', 'date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.student} - {self.group} on {self.date}: {self.get_status_display()}"

    @staticmethod
    def for_group_on_date(group, date):
        """Get all attendance records for a group on a specific date."""
        return Attendance.objects.filter(group=group, date=date)
    
    def get_attendance_percentage(self, start_date=None, end_date=None):
        """Get attendance percentage for a period"""
        from datetime import date, timedelta
        today = date.today()
        end_date = end_date or today
        start_date = start_date or (today - timedelta(days=90))
        
        total = Attendance.objects.filter(
            student=self.student,
            group=self.group,
            date__range=[start_date, end_date]
        ).count()
        
        present = Attendance.objects.filter(
            student=self.student,
            group=self.group,
            date__range=[start_date, end_date],
            status__in=[AttendanceStatus.PRESENT, AttendanceStatus.LATE]
        ).count()
        
        if total == 0:
            return 0
        return (present / total) * 100


# ==================== ADDITIONAL MODELS ====================
class TeacherSalary(models.Model):
    """Track teacher salaries and payments"""
    teacher = models.ForeignKey(
        Teacher,
        related_name='salaries',
        on_delete=models.CASCADE,
        help_text="Teacher"
    )
    month = models.DateField(help_text="Salary month")
    
    # Calculations
    teaching_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Total teaching hours in the month"
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Hourly rate"
    )
    bonus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Additional bonus"
    )
    deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Deductions (taxes, etc.)"
    )
    
    # Total
    total_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total salary to pay"
    )
    
    # Status
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('teacher', 'month')
        ordering = ['-month']

    def __str__(self):
        return f"{self.teacher} - {self.month.strftime('%Y-%m')}"
    
    def calculate_total(self):
        """Recalculate total salary"""
        base = self.teaching_hours * self.hourly_rate
        self.total_salary = base + self.bonus - self.deductions
        return self.total_salary


class LearningCenter(models.Model):
    """Organization/Learning Center information"""
    name = models.CharField(max_length=200, help_text="Learning center name")
    description = models.TextField(blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    address = models.TextField()
    
    # Financial
    currency = models.CharField(
        max_length=10,
        default='UZS',
        help_text="Currency code (UZS, USD, etc.)"
    )
    
    # Settings
    default_tuition_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Default monthly tuition fee"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Learning Centers'

    def __str__(self):
        return self.name


