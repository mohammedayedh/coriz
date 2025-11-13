from django.core.management.base import BaseCommand
from osint_tools.models import OSINTTool


class Command(BaseCommand):
    help = 'إنشاء البيانات الأساسية لأدوات OSINT'

    def handle(self, *args, **options):
        """إنشاء الأدوات الأساسية"""
        
        tools_data = [
            {
                'name': 'GHunt',
                'slug': 'ghunt',
                'description': 'أداة استخبارات Google المتقدمة لجمع المعلومات من خدمات Google المختلفة',
                'tool_type': 'google',
                'icon': 'fab fa-google',
                'color': '#4285f4',
                'requires_auth': True,
                'api_key_required': False,
                'rate_limit': 50,
                'timeout': 60,
                'tool_path': 'GHunt-master',
                'executable_name': 'main.py',
                'command_template': 'python {executable} email {target}',
                'config_schema': {
                    'email_analysis': {'type': 'boolean', 'default': True},
                    'gaia_lookup': {'type': 'boolean', 'default': True},
                    'drive_analysis': {'type': 'boolean', 'default': True},
                },
                'supported_formats': ['json', 'html', 'csv']
            },
            {
                'name': 'Sherlock',
                'slug': 'sherlock',
                'description': 'أداة البحث عن حسابات وسائل التواصل الاجتماعي باستخدام اسم المستخدم',
                'tool_type': 'username',
                'icon': 'fas fa-user-search',
                'color': '#e74c3c',
                'requires_auth': False,
                'api_key_required': False,
                'rate_limit': 100,
                'timeout': 120,
                'tool_path': 'sherlock-master',
                'executable_name': 'sherlock.py',
                'command_template': 'python {executable} {target} --json',
                'config_schema': {
                    'timeout': {'type': 'integer', 'default': 10},
                    'threads': {'type': 'integer', 'default': 20},
                    'verbose': {'type': 'boolean', 'default': False},
                },
                'supported_formats': ['json', 'csv', 'html']
            },
            {
                'name': 'SpiderFoot',
                'slug': 'spiderfoot',
                'description': 'منصة OSINT شاملة مع أكثر من 200 وحدة لجمع المعلومات من مصادر متعددة',
                'tool_type': 'general',
                'icon': 'fas fa-spider',
                'color': '#8e44ad',
                'requires_auth': False,
                'api_key_required': False,
                'rate_limit': 200,
                'timeout': 300,
                'tool_path': 'spiderfoot-master',
                'executable_name': 'sf.py',
                'command_template': 'python {executable} -s {target} -m all -q',
                'config_schema': {
                    'modules': {'type': 'array', 'default': ['all']},
                    'quiet': {'type': 'boolean', 'default': True},
                    'verbose': {'type': 'boolean', 'default': False},
                },
                'supported_formats': ['json', 'csv', 'html', 'xml']
            },
            {
                'name': 'Maigret',
                'slug': 'maigret',
                'description': 'أداة البحث عن الحسابات في مواقع التواصل الاجتماعي والمنصات المختلفة',
                'tool_type': 'username',
                'icon': 'fas fa-search',
                'color': '#27ae60',
                'requires_auth': False,
                'api_key_required': False,
                'rate_limit': 80,
                'timeout': 90,
                'tool_path': 'maigret-master',
                'executable_name': 'maigret',
                'command_template': './{executable} {target} --json',
                'config_schema': {
                    'timeout': {'type': 'integer', 'default': 5},
                    'threads': {'type': 'integer', 'default': 10},
                    'verbose': {'type': 'boolean', 'default': False},
                },
                'supported_formats': ['json', 'csv', 'html']
            },
            {
                'name': 'Infoga',
                'slug': 'infoga',
                'description': 'أداة جمع معلومات البريد الإلكتروني والتحقق من صحته',
                'tool_type': 'email',
                'icon': 'fas fa-envelope',
                'color': '#f39c12',
                'requires_auth': False,
                'api_key_required': False,
                'rate_limit': 60,
                'timeout': 45,
                'tool_path': 'Infoga-master',
                'executable_name': 'infoga.py',
                'command_template': 'python {executable} -i {target}',
                'config_schema': {
                    'verbose': {'type': 'boolean', 'default': True},
                    'timeout': {'type': 'integer', 'default': 10},
                },
                'supported_formats': ['json', 'txt', 'csv']
            },
            {
                'name': 'Harvester',
                'slug': 'harvester',
                'description': 'أداة جمع المعلومات من مصادر مختلفة باستخدام تقنيات متقدمة',
                'tool_type': 'general',
                'icon': 'fas fa-harvest',
                'color': '#34495e',
                'requires_auth': False,
                'api_key_required': False,
                'rate_limit': 150,
                'timeout': 180,
                'tool_path': 'harvester-master',
                'executable_name': 'harvester',
                'command_template': './{executable} -d {target} -b all',
                'config_schema': {
                    'engines': {'type': 'array', 'default': ['all']},
                    'limit': {'type': 'integer', 'default': 100},
                    'verbose': {'type': 'boolean', 'default': False},
                },
                'supported_formats': ['json', 'xml', 'csv', 'html']
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for tool_data in tools_data:
            tool, created = OSINTTool.objects.get_or_create(
                slug=tool_data['slug'],
                defaults=tool_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'تم إنشاء أداة: {tool.name}')
                )
            else:
                # تحديث البيانات الموجودة
                for key, value in tool_data.items():
                    setattr(tool, key, value)
                tool.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'تم تحديث أداة: {tool.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nتم الانتهاء! تم إنشاء {created_count} أداة جديدة وتحديث {updated_count} أداة موجودة.'
            )
        )
