from django.core.management.base import BaseCommand
from osint_tools.models import OSINTTool

class Command(BaseCommand):
    help = 'إضافة أدوات النخبة الاستخباراتية الجديدة للمنصة'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 بدء إضافة أدوات النخبة...'))
        
        pro_tools = [
            {
                'name': 'Breach Detector',
                'slug': 'breach-detector',
                'description': 'فحص تسريبات البيانات العالمية المرتبطة بالبريد الإلكتروني. يحدد قواعد البيانات المسربة ونوع البيانات المكشوفة.',
                'tool_type': 'email',
                'source_type': 'open',
                'required_clearance': 'L2',
                'status': 'active',
                'icon': 'fas fa-user-shield',
                'color': '#ef4444',
                'requires_auth': False,
                'api_key_required': False,
                'rate_limit': 30,
                'timeout': 60,
                'tool_path': 'osint_tools/scrapers',
                'executable_name': 'breach_detector.py',
                'command_template': 'python {tool_path}/{executable_name} {target}',
                'config_schema': {
                    'search_type': 'email',
                    'features': ['كشف قواعد البيانات المسربة', 'تاريخ التسريب', 'نوع البيانات المكشوفة'],
                    'output_fields': ['is_leaked', 'leaks_count', 'sources']
                },
                'supported_formats': ['json']
            },
            {
                'name': 'Social Investigator',
                'slug': 'social-investigator',
                'description': 'محرك بحث اجتماعي شامل يقوم بالتحقق من المعرف (Username) في أكثر من 10 منصات عالمية كبرى واستخراج الروابط المباشرة.',
                'tool_type': 'username',
                'source_type': 'open',
                'required_clearance': 'L2',
                'status': 'active',
                'icon': 'fas fa-search-plus',
                'color': '#3b82f6',
                'requires_auth': False,
                'api_key_required': False,
                'rate_limit': 20,
                'timeout': 120,
                'tool_path': 'osint_tools/scrapers',
                'executable_name': 'social_investigator.py',
                'command_template': 'python {tool_path}/{executable_name} {target}',
                'config_schema': {
                    'search_type': 'username',
                    'features': ['مسح متوازي للمنصات', 'روابط بروفايلات مباشرة', 'كشف الحسابات النشطة'],
                    'output_fields': ['total_found', 'found_accounts']
                },
                'supported_formats': ['json']
            },
            {
                'name': 'Company Intelligence',
                'slug': 'company-intel',
                'description': 'البحث في السجلات القانونية للشركات حول العالم. يستخرج بيانات المؤسسين، العناوين القانونية، والحالة التشغيلية.',
                'tool_type': 'general',
                'source_type': 'open',
                'required_clearance': 'L3',
                'status': 'active',
                'icon': 'fas fa-building',
                'color': '#10b981',
                'requires_auth': False,
                'api_key_required': False,
                'rate_limit': 50,
                'timeout': 60,
                'tool_path': 'osint_tools/scrapers',
                'executable_name': 'company_intel.py',
                'command_template': 'python {tool_path}/{executable_name} {target}',
                'config_schema': {
                    'search_type': 'company name',
                    'features': ['سجلات قانونية دولية', 'بيانات الملاك والمؤسسين', 'الحالة القانونية'],
                    'output_fields': ['total_results', 'companies']
                },
                'supported_formats': ['json']
            }
        ]

        for tool_data in pro_tools:
            tool, created = OSINTTool.objects.update_or_create(
                slug=tool_data['slug'],
                defaults=tool_data
            )
            status = 'إضافة' if created else 'تحديث'
            self.stdout.write(self.style.SUCCESS(f'✅ تم {status}: {tool.name}'))

        self.stdout.write(self.style.SUCCESS('✨ اكتملت عملية تسجيل أدوات النخبة بنجاح!'))
