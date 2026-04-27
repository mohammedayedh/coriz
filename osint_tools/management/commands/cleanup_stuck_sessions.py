"""
أمر Django لتنظيف الجلسات العالقة
يمكن تشغيله يدوياً أو جدولته عبر cron
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from osint_tools.models import OSINTSession


class Command(BaseCommand):
    help = 'تنظيف الجلسات العالقة في حالة "running" لأكثر من 10 دقائق'

    def add_arguments(self, parser):
        parser.add_argument(
            '--minutes',
            type=int,
            default=10,
            help='عدد الدقائق لاعتبار الجلسة عالقة (افتراضي: 10)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='عرض الجلسات التي سيتم تنظيفها بدون تنفيذ'
        )

    def handle(self, *args, **options):
        minutes = options['minutes']
        dry_run = options['dry_run']
        
        # حساب الوقت الحد
        cutoff_time = timezone.now() - timedelta(minutes=minutes)
        
        # البحث عن الجلسات العالقة
        stuck_sessions = OSINTSession.objects.filter(
            status__in=['pending', 'running'],
            updated_at__lt=cutoff_time
        )
        
        count = stuck_sessions.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('✓ لا توجد جلسات عالقة')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'تم العثور على {count} جلسة عالقة:')
        )
        
        for session in stuck_sessions:
            age = timezone.now() - session.updated_at
            self.stdout.write(
                f'  - جلسة #{session.id}: {session.tool.name} - {session.target} '
                f'(عالقة منذ {age.seconds // 60} دقيقة)'
            )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n⚠ وضع التجربة - لم يتم تنفيذ أي تغييرات')
            )
            return
        
        # تحديث الجلسات العالقة
        updated = stuck_sessions.update(
            status='failed',
            error_message=f'تم إلغاء الجلسة تلقائياً - عالقة لأكثر من {minutes} دقيقة',
            current_step='تم الإلغاء تلقائياً',
            completed_at=timezone.now()
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ تم تنظيف {updated} جلسة عالقة')
        )
