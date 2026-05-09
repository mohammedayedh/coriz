"""
أمر Django لإضافة أداة Have I Been Pwned إلى قاعدة البيانات
"""

from django.core.management.base import BaseCommand
from osint_tools.models import OSINTTool


class Command(BaseCommand):
    help = 'إضافة أداة Have I Been Pwned (HIBP) إلى قاعدة البيانات'

    def handle(self, *args, **options):
        self.stdout.write('🔍 إضافة Have I Been Pwned (HIBP)...')
        
        tool, created = OSINTTool.objects.update_or_create(
            slug='hibp',
            defaults={
                'name': 'Have I Been Pwned',
                'description': 'محرك بحث عن التسريبات الأمنية وقواعد البيانات المخترقة. يحتوي على أكثر من 12 مليار حساب مسرب من آلاف التسريبات الأمنية. يوفر معلومات تفصيلية عن كل تسريب والبحث في مواقع Paste وفحص كلمات المرور المخترقة. مجاني 100% ولا يحتاج API key.',
                'tool_type': 'email',
                'source_type': 'open',
                'required_clearance': 'L1',
                'status': 'active',
                'icon': 'fas fa-shield-alt',
                'color': '#00a8cc',
                'requires_auth': False,
                'api_key_required': False,
                'rate_limit': 40,
                'timeout': 30,
                'tool_path': 'hibp_scraper',  # يعمل عبر scraper مباشر
                'executable_name': 'HIBPScraper',  # اسم الـ class
                'command_template': 'python_scraper',  # علامة أنه scraper مباشر
                'config_schema': {
                    'check_breaches': {
                        'type': 'boolean',
                        'default': True,
                        'description': 'البحث في قاعدة بيانات التسريبات'
                    },
                    'check_pastes': {
                        'type': 'boolean',
                        'default': True,
                        'description': 'البحث في مواقع Paste'
                    },
                    'include_unverified': {
                        'type': 'boolean',
                        'default': True,
                        'description': 'تضمين التسريبات غير المؤكدة'
                    }
                }
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
