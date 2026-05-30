import logging
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST
import json

from core.models import Group, Student, Payment, Attendance, StudentStatus, PaymentStatus
from .forms import StudentSignUpForm

logger = logging.getLogger(__name__)


def is_operator_user(user):
    """Operator access includes staff/admin users and users with operator/admin profile roles."""
    if not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    profile = getattr(user, 'profile', None)
    return bool(profile and profile.role in ('operator', 'admin'))


def user_role(user):
    if not user.is_authenticated:
        return ''
    if user.is_superuser:
        return 'admin'
    profile = getattr(user, 'profile', None)
    return getattr(profile, 'role', '') or ''


def is_teacher_user(user):
    return user.is_authenticated and user_role(user) == 'teacher'


@ensure_csrf_cookie
def operator_session(request):
    """Return current operator session state and set a CSRF cookie."""
    user = request.user
    role = user_role(user)
    return JsonResponse({
        'authenticated': user.is_authenticated,
        'is_operator': is_operator_user(user),
        'is_teacher': is_teacher_user(user),
        'role': role,
        'username': user.username if user.is_authenticated else '',
        'full_name': user.get_full_name() if user.is_authenticated else '',
    })


@csrf_exempt
@require_POST
def operator_login(request):
    """Session login endpoint for the React operator cabinet."""
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'Invalid JSON payload.'}, status=400)

    username = payload.get('username', '')
    password = payload.get('password', '')
    user = authenticate(request, username=username, password=password)

    if user is None:
        return JsonResponse({'detail': 'Login yoki parol noto\'g\'ri.'}, status=400)
    if not (is_operator_user(user) or is_teacher_user(user)):
        return JsonResponse({'detail': 'Bu kabinetga faqat operator yoki o\'qituvchi kirishi mumkin.'}, status=403)

    login(request, user)
    role = user_role(user)
    return JsonResponse({
        'authenticated': True,
        'is_operator': is_operator_user(user),
        'is_teacher': is_teacher_user(user),
        'role': role,
        'username': user.username,
        'full_name': user.get_full_name(),
    })


@csrf_exempt
@require_POST
def operator_logout(request):
    """Logout endpoint for the React operator cabinet."""
    logout(request)
    return JsonResponse({'authenticated': False, 'is_operator': False, 'is_teacher': False, 'role': ''})


def home(request):
    """Home/landing page with role-based navigation."""
    profile = getattr(request.user, 'profile', None) if request.user.is_authenticated else None
    context = {
        'user': request.user,
        'profile': profile,
        'is_staff': request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser),
        'stats': {
            'students': Student.objects.filter(status=StudentStatus.ACTIVE).count(),
            'groups': Group.objects.filter(is_active=True).count(),
            'payments_pending': Payment.objects.filter(status__in=[PaymentStatus.PENDING, PaymentStatus.OVERDUE]).count(),
        },
    }
    return render(request, 'accounts/home.html', context)


def student_signup(request):
    """Register a new student account."""
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                user.first_name = form.cleaned_data.get('first_name')
                user.last_name = form.cleaned_data.get('last_name')
                user.email = form.cleaned_data.get('email')
                user.save()
                
                # Set profile role and phone
                profile = user.profile
                profile.role = 'student'
                profile.phone = form.cleaned_data.get('phone', '')
                profile.save()
                
                # Create Student record linked to user
                Student.objects.create(
                    user=user,
                    first_name=user.first_name or user.username,
                    last_name=user.last_name,
                    phone=profile.phone,
                    group=None
                )
                
                login(request, user)
                messages.success(request, 'Account created successfully! Welcome!')
                logger.info(f"New student registered: {user.username}")
                return redirect('student-dashboard')
            except Exception as e:
                logger.error(f"Error creating student account: {str(e)}")
                messages.error(request, 'An error occurred during registration. Please try again.')
    else:
        form = StudentSignUpForm()
    
    return render(request, 'accounts/student_signup.html', {'form': form})


@login_required(login_url='login')
def student_dashboard(request):
    """Student dashboard with their group and payment info."""
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'student':
        logger.warning(f"Unauthorized access to student dashboard by user {request.user.username}")
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    try:
        student = request.user.student_profile
        context = {
            'student': student,
            'group': student.group,
            'recent_payments': student.payments.select_related('group')[:6],
            'recent_attendances': student.attendances.select_related('group')[:10],
        }
        return render(request, 'accounts/student_dashboard.html', context)
    except Student.DoesNotExist:
        logger.error(f"Student profile not found for user {request.user.username}")
        messages.error(request, 'Student profile not found.')
        return redirect('home')


@login_required(login_url='login')
def teacher_dashboard(request):
    """Teacher dashboard with assigned groups and students."""
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'teacher':
        logger.warning(f"Unauthorized access to teacher dashboard by user {request.user.username}")
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    try:
        # Get groups assigned to this teacher via the Teacher model relationship
        teacher_profile = request.user.teacher_profile
        groups = teacher_profile.groups.prefetch_related('students').all()
        student_count = Student.objects.filter(group__teacher=teacher_profile).count()
        
        context = {
            'groups': groups,
            'teacher': teacher_profile,
            'student_count': student_count,
        }
        return render(request, 'accounts/teacher_dashboard.html', context)
    except Exception as e:
        logger.error(f"Error loading teacher dashboard for {request.user.username}: {str(e)}")
        messages.error(request, 'An error occurred loading your dashboard.')
        return redirect('home')

