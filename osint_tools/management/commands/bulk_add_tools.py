"""
أمر Django لإضافة أدوات OSINT بشكل جماعي من ملف JSON
الاستخدام: python manage.py bulk_add_tools tools_data.json
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from osint_tools.models import OSINTTool
import json
import os


class Command(BaseCommand):
    help = 'إضافة أدوات OSINT بشكل جماعي من ملف JSON'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='مسار ملف JSON الذي يحتوي على بيانات الأدوات'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='تحديث الأدوات الموجودة بدلاً من تخطيها'
        )

    def handle(self, *args, **options):
        json_file = options['json_file']
        update_existing = options['update']

        if not os.path.exists(json_file):
            self.stdout.write(self.style.ERROR(f'الملف غير موجود: {json_file}'))
            return

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                tools_data = json.load(f)
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'خطأ في قراءة JSON: {e}'))
            return

        if not isinstance(tools_data, list):
            self.stdout.write(self.style.ERROR('يجب أن يكون الملف عبارة عن قائمة من الأدوات'))
            return

        added_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0

        for tool_data in tools_data:
            try:
                name = tool_data.get('name')
                if not name:
                    self.stdout.write(self.style.WARNING('تخطي أداة بدون اسم'))
                    skipped_count += 1
                    continue

                slug = tool_data.get('slug', slugify(name))
                
                # التحقق من وجود الأداة
                existing_tool = OSINTTool.objects.filter(slug=slug).first()
                
                if existing_tool:
                    if update_existing:
                        # تحديث الأداة الموجودة
                        for key, value in tool_data.items():
                            if key != 'slug':  # لا نحدث slug
                                setattr(existing_tool, key, value)
                        existing_tool.save()
                        self.stdout.write(
                            self.style.SUCCESS(f'✅ تم تحديث: {name}')
                        )
                        updated_count += 1
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'⏭️  موجود مسبقاً: {name}')
                        )
                        skipped_count += 1
                else:
                    # إنشاء أداة جديدة
                    tool = OSINTTool.objects.create(
                        name=name,
                        slug=slug,
                        description=tool_data.get('description', ''),
                        tool_type=tool_data.get('tool_type', 'general'),
                        source_type=tool_data.get('source_type', 'open'),
                        required_clearance=tool_data.get('required_clearance', 'L1'),
                        status=tool_data.get('status', 'active'),
                        icon=tool_data.get('icon', 'fas fa-search'),
                        color=tool_data.get('color', '#007bff'),
                        requires_auth=tool_data.get('requires_auth', False),
                        api_key_required=tool_data.get('api_key_required', False),
                        rate_limit=tool_data.get('rate_limit', 100),
                        timeout=tool_data.get('timeout', 30),
                        tool_path=tool_data.get('tool_path', ''),
                        executable_name=tool_data.get('executable_name', name.lower()),
                        command_template=tool_data.get('command_template', ''),
                        config_schema=tool_data.get('config_schema', {}),
                        supported_formats=tool_data.get('supported_formats', [])
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ تمت الإضافة: {name}')
                    )
                    added_count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ خطأ في إضافة {tool_data.get("name", "unknown")}: {e}')
                )
                error_count += 1

        # ملخص النتائج
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'✅ تمت الإضافة: {added_count}'))
        if updated_count > 0:
            self.stdout.write(self.style.SUCCESS(f'🔄 تم التحديث: {updated_count}'))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f'⏭️  تم التخطي: {skipped_count}'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'❌ أخطاء: {error_count}'))
        self.stdout.write('='*50)
