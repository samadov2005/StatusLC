"""
Django management command to generate monthly reports.
Usage: python manage.py monthly_report --month=2026-04
"""

from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandError

from core.models import Group, PaymentStatus, Student, StudentStatus
from core.utils import get_month_attendance_summary, get_unpaid_students


class Command(BaseCommand):
    help = 'Generate monthly reports for payments and attendance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            type=str,
            help='Month in YYYY-MM format (default: current month)',
        )
        parser.add_argument(
            '--group',
            type=int,
            help='Generate report for specific group ID (optional)',
        )
        parser.add_argument(
            '--output',
            type=str,
            default='csv',
            help='Output format: csv or json (default: csv)',
        )

    def handle(self, *args, **options):
        if options['month']:
            try:
                month_date = datetime.strptime(options['month'], '%Y-%m').date().replace(day=1)
            except ValueError:
                raise CommandError('Invalid month format. Use YYYY-MM (e.g., 2026-04)')
        else:
            month_date = date.today().replace(day=1)

        self.stdout.write(
            self.style.SUCCESS(f'\nMonthly report for {month_date.strftime("%B %Y")}')
        )

        unpaid_students = get_unpaid_students(month_date)
        paid_students = Student.objects.filter(
            payments__month=month_date,
            payments__status=PaymentStatus.PAID,
            status=StudentStatus.ACTIVE,
        ).distinct()

        total_students = Student.objects.filter(status=StudentStatus.ACTIVE).count()
        total_paid = paid_students.count()
        total_unpaid = unpaid_students.count()

        self.stdout.write('\nPayment summary:')
        self.stdout.write(f'  Total students: {total_students}')
        self.stdout.write(
            self.style.SUCCESS(
                f'  Paid: {total_paid} ({total_paid * 100 // total_students if total_students > 0 else 0}%)'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                f'  Unpaid: {total_unpaid} ({total_unpaid * 100 // total_students if total_students > 0 else 0}%)'
            )
        )

        if unpaid_students.exists():
            self.stdout.write('\nUnpaid students:')
            for student in unpaid_students:
                self.stdout.write(f'  - {student.full_name} ({student.phone})')

        if options['group']:
            try:
                group = Group.objects.get(id=options['group'])
                summary = get_month_attendance_summary(group, month_date)

                self.stdout.write(f'\nAttendance for {group.name}:')
                self.stdout.write(f'  Present: {summary["total_present"]}')
                self.stdout.write(f'  Absent: {summary["total_absent"]}')
                self.stdout.write(f'  Excused: {summary["total_excused"]}')

                for stats in summary['students'].values():
                    rate = f"{stats['attendance_rate']:.1f}%"
                    self.stdout.write(
                        f'  - {stats["student"].full_name}: '
                        f'{stats["present"]}/{stats["total"]} ({rate})'
                    )
            except Group.DoesNotExist:
                raise CommandError(f'Group with ID {options["group"]} not found')

        self.stdout.write(self.style.SUCCESS('Report generated successfully.\n'))
