import os
import django

from osint_tools.models import OSINTTool

tools_to_add = [
    {
        'name': 'Phone Number Analyzer',
        'slug': 'phone-analyzer',
        'description': 'تحليل أرقام الهواتف الدولية لمعرفة الدولة، المنطقة، مزود الخدمة، والمنطقة الزمنية بدقة عالية.',
        'tool_type': 'phone',
        'required_clearance': 'L1',
        'status': 'active',
        'icon': 'fas fa-phone-alt',
        'tool_path': '/osint/intel/phone-analyzer/',
        'executable_name': 'python_api',
        'command_template': 'internal'
    },
    {
        'name': 'Subdomain Enumerator',
        'slug': 'subdomain-enum',
        'description': 'استخراج النطاقات الفرعية العميقة لأي موقع عبر تحليل قوائم الشفافية لشهادات الأمان (crt.sh).',
        'tool_type': 'domain',
        'required_clearance': 'L1',
        'status': 'active',
        'icon': 'fas fa-sitemap',
        'tool_path': '/osint/intel/subdomain-enum/',
        'executable_name': 'python_api',
        'command_template': 'internal'
    }
]

added = 0
for tool_data in tools_to_add:
    tool, created = OSINTTool.objects.get_or_create(slug=tool_data['slug'], defaults=tool_data)
    if created:
        print(f"Created: {tool.name}")
        added += 1
    else:
        # Update existing properties if needed
        for key, value in tool_data.items():
            setattr(tool, key, value)
        tool.save()
        print(f"Updated: {tool.name}")

print(f"Successfully processed {len(tools_to_add)} tools.")
