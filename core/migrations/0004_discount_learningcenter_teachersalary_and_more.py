import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0003_alter_attendance_options_alter_group_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Discount name', max_length=200)),
                ('description', models.TextField(blank=True)),
                ('discount_type', models.CharField(choices=[('percentage', 'Foiz (Percentage)'), ('fixed', 'Soʻm (Fixed Amount)')], max_length=50)),
                ('value', models.DecimalField(decimal_places=2, help_text='Discount value (% or amount)', max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='LearningCenter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Learning center name', max_length=200)),
                ('description', models.TextField(blank=True)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=30)),
                ('address', models.TextField()),
                ('currency', models.CharField(default='UZS', help_text='Currency code (UZS, USD, etc.)', max_length=10)),
                ('default_tuition_fee', models.DecimalField(decimal_places=2, default=0, help_text='Default monthly tuition fee', max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Learning Centers',
            },
        ),
        migrations.CreateModel(
            name='TeacherSalary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.DateField(help_text='Salary month')),
                ('teaching_hours', models.DecimalField(decimal_places=2, default=0, help_text='Total teaching hours in the month', max_digits=10)),
                ('hourly_rate', models.DecimalField(decimal_places=2, help_text='Hourly rate', max_digits=10)),
                ('bonus', models.DecimalField(decimal_places=2, default=0, help_text='Additional bonus', max_digits=10)),
                ('deductions', models.DecimalField(decimal_places=2, default=0, help_text='Deductions (taxes, etc.)', max_digits=10)),
                ('total_salary', models.DecimalField(decimal_places=2, help_text='Total salary to pay', max_digits=10)),
                ('is_paid', models.BooleanField(default=False)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-month'],
            },
        ),
        migrations.AlterModelOptions(
            name='teacher',
            options={'ordering': ['first_name', 'last_name'], 'verbose_name': 'Teacher', 'verbose_name_plural': 'Teachers'},
        ),
        migrations.AlterUniqueTogether(
            name='payment',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='attendance',
            name='present',
        ),
        migrations.RemoveField(
            model_name='group',
            name='time',
        ),
        migrations.AddField(
            model_name='attendance',
            name='minutes_present',
            field=models.IntegerField(default=0, help_text='Minutes present in class (0 if not tracked)', validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='attendance',
            name='recorded_by',
            field=models.ForeignKey(blank=True, help_text='User who recorded attendance', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recorded_attendances', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='attendance',
            name='status',
            field=models.CharField(choices=[('present', 'Hozir (Present)'), ('absent', "Yo'q (Absent)"), ('late', 'Kechiktirgan (Late)'), ('excused', 'Bujanishli (Excused)')], default='present', help_text='Attendance status', max_length=20),
        ),
        migrations.AddField(
            model_name='group',
            name='day_of_week',
            field=models.CharField(blank=True, choices=[('monday', 'Dushanba (Monday)'), ('tuesday', 'Seshanba (Tuesday)'), ('wednesday', 'Chorshanba (Wednesday)'), ('thursday', 'Payshanba (Thursday)'), ('friday', 'Juma (Friday)'), ('saturday', 'Shanba (Saturday)'), ('sunday', 'Yakshanba (Sunday)')], help_text='Day of week for classes', max_length=20),
        ),
        migrations.AddField(
            model_name='group',
            name='description',
            field=models.TextField(blank=True, help_text='Group description and objectives'),
        ),
        migrations.AddField(
            model_name='group',
            name='end_date',
            field=models.DateField(blank=True, help_text='Group end date (if completed)', null=True),
        ),
        migrations.AddField(
            model_name='group',
            name='end_time',
            field=models.TimeField(default=datetime.time(19, 32, 44, 354265), help_text='Class end time (e.g., 19:30)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='group',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Is the group currently active?'),
        ),
        migrations.AddField(
            model_name='group',
            name='max_students',
            field=models.IntegerField(default=20, help_text='Maximum number of students', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AddField(
            model_name='group',
            name='min_students',
            field=models.IntegerField(default=5, help_text='Minimum students to keep group active', validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='group',
            name='start_date',
            field=models.DateField(default=django.utils.timezone.now, help_text='Group start date'),
        ),
        migrations.AddField(
            model_name='group',
            name='start_time',
            field=models.TimeField(default=datetime.time(19, 32, 52, 617232), help_text='Class start time (e.g., 18:00)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='group',
            name='tuition_fee',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Monthly tuition fee per student', max_digits=10, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='payment',
            name='confirmed_at',
            field=models.DateTimeField(blank=True, help_text='When payment was confirmed', null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='created_by',
            field=models.ForeignKey(blank=True, help_text='User who recorded the payment', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_payments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='payment',
            name='group',
            field=models.ForeignKey(help_text='Group for which payment is made', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='core.group'),
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_method',
            field=models.CharField(choices=[('cash', 'Naqd (Cash)'), ('card', 'Karta (Card)'), ('transfer', "O'tkazma (Transfer)"), ('mobile', 'Mobil (Mobile)'), ('other', 'Boshqa (Other)')], default='cash', help_text='Payment method', max_length=50),
        ),
        migrations.AddField(
            model_name='payment',
            name='reference_number',
            field=models.CharField(blank=True, help_text='Transaction/receipt reference number', max_length=100),
        ),
        migrations.AddField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[('paid', "To'langan (Paid)"), ('pending', 'Kutilmoqda (Pending)'), ('overdue', "Muddati O'tgan (Overdue)"), ('partial', 'Qisman (Partial)')], default='pending', help_text='Payment status', max_length=20),
        ),
        migrations.AddField(
            model_name='student',
            name='date_of_birth',
            field=models.DateField(blank=True, help_text="Student's date of birth", null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='email',
            field=models.EmailField(blank=True, help_text="Student's email address", max_length=254),
        ),
        migrations.AddField(
            model_name='student',
            name='enrollment_date',
            field=models.DateField(default=django.utils.timezone.now, help_text='Date student enrolled'),
        ),
        migrations.AddField(
            model_name='student',
            name='parent_email',
            field=models.EmailField(blank=True, help_text='Parent/Guardian email', max_length=254),
        ),
        migrations.AddField(
            model_name='student',
            name='parent_name',
            field=models.CharField(blank=True, help_text='Parent/Guardian name', max_length=200),
        ),
        migrations.AddField(
            model_name='student',
            name='status',
            field=models.CharField(choices=[('active', 'Faol (Active)'), ('inactive', 'Nofaol (Inactive)'), ('graduated', 'Bitirgan (Graduated)'), ('suspended', "To'xtatilgan (Suspended)"), ('dropped', 'Tark etgan (Dropped)')], default='active', help_text='Enrollment status', max_length=20),
        ),
        migrations.AddField(
            model_name='teacher',
            name='address',
            field=models.TextField(blank=True, help_text='Physical address'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='created_by',
            field=models.ForeignKey(blank=True, help_text='User who created this record', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_teachers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='teacher',
            name='email',
            field=models.EmailField(default='noemail@example.com', help_text="Teacher's email address", max_length=254, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='teacher',
            name='hire_date',
            field=models.DateField(default=datetime.date(2026, 4, 18), help_text='Date hired'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='teacher',
            name='hourly_rate',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Hourly rate in local currency', max_digits=10, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='teacher',
            name='status',
            field=models.CharField(choices=[('active', 'Faol (Active)'), ('inactive', 'Nofaol (Inactive)'), ('leave', "Ta'tilda (On Leave)"), ('terminated', 'Ishdan chiqarilgan (Terminated)')], default='active', help_text='Employment status', max_length=20),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='note',
            field=models.CharField(blank=True, help_text='Reason for absence or late arrival', max_length=200),
        ),
        migrations.AlterField(
            model_name='group',
            name='level',
            field=models.CharField(help_text='Proficiency level (A1, A2, B1, etc.)', max_length=100),
        ),
        migrations.AlterField(
            model_name='payment',
            name='amount',
            field=models.DecimalField(decimal_places=2, help_text='Payment amount in local currency', max_digits=10, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='month',
            field=models.DateField(help_text='Month for payment (use 1st day of month)'),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='phone',
            field=models.CharField(help_text='Phone number for contact', max_length=30),
        ),
        migrations.AlterUniqueTogether(
            name='payment',
            unique_together={('student', 'group', 'month')},
        ),
        migrations.AddIndex(
            model_name='attendance',
            index=models.Index(fields=['status'], name='core_attend_status_8c6988_idx'),
        ),
        migrations.AddIndex(
            model_name='group',
            index=models.Index(fields=['is_active'], name='core_group_is_acti_abdf64_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['status'], name='core_paymen_status_8390cc_idx'),
        ),
        migrations.AddIndex(
            model_name='student',
            index=models.Index(fields=['status'], name='core_studen_status_c9d890_idx'),
        ),
        migrations.AddIndex(
            model_name='student',
            index=models.Index(fields=['phone'], name='core_studen_phone_d6a640_idx'),
        ),
        migrations.AddIndex(
            model_name='teacher',
            index=models.Index(fields=['status'], name='core_teache_status_cecf7b_idx'),
        ),
        migrations.AddIndex(
            model_name='teacher',
            index=models.Index(fields=['email'], name='core_teache_email_0ea460_idx'),
        ),
        migrations.AddField(
            model_name='teachersalary',
            name='teacher',
            field=models.ForeignKey(help_text='Teacher', on_delete=django.db.models.deletion.CASCADE, related_name='salaries', to='core.teacher'),
        ),
        migrations.AddField(
            model_name='discount',
            name='applicable_groups',
            field=models.ManyToManyField(blank=True, help_text='Groups where discount applies (leave empty for all)', to='core.group'),
        ),
        migrations.AddField(
            model_name='discount',
            name='applicable_students',
            field=models.ManyToManyField(blank=True, help_text='Students who get this discount (leave empty for all)', to='core.student'),
        ),
        migrations.AlterUniqueTogether(
            name='teachersalary',
            unique_together={('teacher', 'month')},
        ),
    ]
