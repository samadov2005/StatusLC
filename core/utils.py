"""
Utility functions for the core app.
"""
from datetime import date, timedelta
from django.utils.dateparse import parse_date
from .models import Student, Payment, Attendance, AttendanceStatus, PaymentStatus, StudentStatus


def get_unpaid_students(month_date):
    """
    Get all students who have NOT paid for a given month.
    
    Args:
        month_date: datetime.date object representing any date in the target month
        
    Returns:
        QuerySet of unpaid Student objects
        
    Example:
        unpaid = get_unpaid_students(date(2026, 4, 1))
    """
    paid_student_ids = Payment.objects.filter(
        month=month_date,
        status=PaymentStatus.PAID
    ).values_list(
        'student_id', flat=True
    )
    return Student.objects.filter(status=StudentStatus.ACTIVE).exclude(id__in=paid_student_ids)


def get_month_attendance_summary(group, month_date):
    """
    Get attendance summary for a group for a specific month.
    
    Args:
        group: Group object
        month_date: datetime.date object representing any date in the target month
        
    Returns:
        dict with attendance statistics
    """
    # Get all days in the month
    if month_date.month == 12:
        next_month = month_date.replace(year=month_date.year + 1, month=1, day=1)
    else:
        next_month = month_date.replace(month=month_date.month + 1, day=1)
    
    month_start = month_date.replace(day=1)
    
    # Get attendance records for the month
    attendances = Attendance.objects.filter(
        group=group,
        date__gte=month_start,
        date__lt=next_month
    )
    
    total_classes = attendances.values('date').distinct().count()
    present_statuses = [AttendanceStatus.PRESENT, AttendanceStatus.LATE]
    
    summary = {
        'group': group,
        'month': month_date,
        'total_classes': total_classes,
        'total_present': attendances.filter(status__in=present_statuses).count(),
        'total_absent': attendances.filter(status=AttendanceStatus.ABSENT).count(),
        'total_excused': attendances.filter(status=AttendanceStatus.EXCUSED).count(),
        'students': {}
    }
    
    # Breakdown by student
    for student in group.students.all():
        student_attendance = attendances.filter(student=student)
        summary['students'][student.id] = {
            'student': student,
            'present': student_attendance.filter(status__in=present_statuses).count(),
            'absent': student_attendance.filter(status=AttendanceStatus.ABSENT).count(),
            'excused': student_attendance.filter(status=AttendanceStatus.EXCUSED).count(),
            'total': student_attendance.count(),
            'attendance_rate': (
                (student_attendance.filter(status__in=present_statuses).count() / total_classes * 100)
                if total_classes > 0 else 0
            )
        }
    
    return summary


def mark_attendance_for_group(group, attendance_date, present_student_ids=None):
    """
    Mark attendance for all students in a group on a specific date.
    Students not in present_student_ids are marked as absent.
    
    Args:
        group: Group object
        attendance_date: datetime.date object
        present_student_ids: list of student IDs who were present (default: empty = all absent)
        
    Returns:
        tuple of (created_count, updated_count)
    """
    if present_student_ids is None:
        present_student_ids = []
    
    created_count = 0
    updated_count = 0
    
    for student in group.students.all():
        attendance_status = (
            AttendanceStatus.PRESENT
            if student.id in present_student_ids
            else AttendanceStatus.ABSENT
        )
        attendance, created = Attendance.objects.update_or_create(
            student=student,
            group=group,
            date=attendance_date,
            defaults={'status': attendance_status}
        )
        if created:
            created_count += 1
        else:
            updated_count += 1
    
    return created_count, updated_count


def calculate_payment_status(student):
    """
    Get payment status for a student (current month).
    
    Args:
        student: Student object
        
    Returns:
        dict with payment information
    """
    today = date.today()
    current_month = today.replace(day=1)
    
    payment = Payment.objects.filter(
        student=student,
        month=current_month
    ).first()
    
    return {
        'student': student,
        'month': current_month,
        'paid': payment is not None and payment.status == PaymentStatus.PAID,
        'payment': payment,
        'amount': payment.amount if payment else None,
        'paid_at': payment.paid_at if payment else None
    }
