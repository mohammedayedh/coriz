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
                'description': 'محرك بحث عن التسريبات الأمنية وقواعد البيانات المخترقة. يحتوي على أكثر من 12 مليار حساب مسرب من آلاف التسريبات الأمنية',
                'tool_type': 'email',
                'source_type': 'open',
                'required_clearance': 'L1',
                'status': 'active',
                'icon': 'fas fa-shield-alt',
                'color': '#00a8cc',
                'requires_auth': False,
                'api_key_required': False,
                'rate_limit': 40,  # 40 طلب/دقيقة (مع rate limiting داخلي)
                'timeout': 30,
                'tool_path': '',  # يعمل مباشرة عبر scraper
                'executable_name': '',
                'command_template': '',
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
                },
                'input_types': ['email'],
                'output_format': 'json',
                'documentation_url': 'https://haveibeenpwned.com/API/v3',
                'example_usage': 'أدخل عنوان بريد إلكتروني للبحث عن التسريبات المرتبطة به',
                'tags': ['breach', 'leak', 'security', 'email', 'password', 'data-breach'],
                'features': [
                    'البحث في أكثر من 12 مليار حساب مسرب',
                    'معلومات تفصيلية عن كل تسريب',
                    'البحث في مواقع Paste',
                    'فحص كلمات المرور المخترقة',
                    'مجاني 100% - لا يحتاج API key',
                    'تحديثات مستمرة'
                ],
                'limitations': [
                    'Rate Limiting: طلب واحد كل 1.5 ثانية',
                    'لا يعرض كلمات المرور المسربة (لأسباب أمنية)',
                    'يعرض فقط التسريبات المعروفة والموثقة'
                ],
                'use_cases': [
                    'التحقق من أمان البريد الإلكتروني',
                    'اكتشاف التسريبات الأمنية',
                    'تقييم المخاطر الأمنية',
                    'التحقيق في الحوادث الأمنية',
                    'مراقبة أمان الحسابات'
                ]
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
