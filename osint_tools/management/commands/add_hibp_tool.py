"""
أمر Django لإضافة أداة Have I Been Pwned إلى قاعدة البيانات
"""

from django.core.management.base import BaseCommand
from osint_tools.models import OSINTTool


class Command(BaseCommand):
    help = 'إضافة أداة Have I Been Pwned (HIBP) إلى قاعدة البيانات'

    def handle(self, *args, **options):
        self.stdout.write('🔍 إضافة Password Pwned Checker (HIBP)...')
        
        tool, created = OSINTTool.objects.update_or_create(
            slug='hibp',
            defaults={
                'name': 'Password Pwned Checker',
                'description': 'فحص كلمات المرور في قاعدة بيانات Have I Been Pwned - أكثر من 850 مليون كلمة مرور مخترقة. يستخدم k-Anonymity لحماية خصوصيتك (لا يرسل كلمة المرور كاملة). مجاني 100% ولا يحتاج API key.',
                'tool_type': 'general',
                'source_type': 'open',
                'required_clearance': 'L1',
                'status': 'active',
                'icon': 'fas fa-key',
                'color': '#e74c3c',
                'requires_auth': False,
                'api_key_required': False,
                'rate_limit': 100,
                'timeout': 30,
                'tool_path': 'hibp_scraper',
                'executable_name': 'HIBPScraper',
                'command_template': 'python_scraper',
                'config_schema': {}
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ تم إنشاء أداة {tool.name} بنجاح'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✅ تم تحديث أداة {tool.name} بنجاح'))
        
        self.stdout.write(f'   الـ slug: {tool.slug}')
        self.stdout.write(f'   النوع: {tool.tool_type}')
        self.stdout.write(f'   الحالة: {tool.status}')
        self.stdout.write(f'   الرابط: /osint/tools/{tool.slug}/')
        
        self.stdout.write(self.style.SUCCESS('\n🎉 تم بنجاح!'))
