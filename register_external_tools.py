import os
import django
import sys

# إعداد بيئة دجانجو
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coriza.settings')
django.setup()

from osint_tools.models import OSINTTool

tools_to_add = [
    {
        'name': 'MxToolbox DNS & Email Analyzer',
        'slug': 'mxtoolbox-pro',
        'description': 'فحص شامل لنطاقات وخوادم البريد الإلكتروني عبر خوارزميات MxToolbox واستخراج سجلات DNS وسمعة الـ IP.',
        'tool_type': 'domain',
        'required_clearance': 'L1',
        'status': 'active',
        'icon': 'fas fa-network-wired',
        'tool_path': '/osint/intel/mxtoolbox-pro/',
        'executable_name': 'python3',
        'command_template': 'python3 osint_tools/adapters/mxtoolbox_adapter.py {target}'
    },
    {
        'name': 'HudsonRock Infostealer Search',
        'slug': 'hudsonrock-pro',
        'description': 'البحث المتقدم في قواعد بيانات HudsonRock للتحقق مما إذا كان الهدف (إيميل، دومين، IP) قد تعرض لاختراق وسرقة بيانات.',
        'tool_type': 'email',
        'required_clearance': 'L2',
        'status': 'active',
        'icon': 'fas fa-user-secret',
        'tool_path': '/osint/intel/hudsonrock-pro/',
        'executable_name': 'python3',
        'command_template': 'python3 osint_tools/adapters/hudsonrock_adapter.py {target}'
    },
    {
        'name': 'Holehe Account OSINT',
        'slug': 'holehe-pro',
        'description': 'البحث عن الحسابات المسجلة بنفس البريد الإلكتروني في أكثر من 120 موقع وخدمة حول العالم.',
        'tool_type': 'email',
        'required_clearance': 'L1',
        'status': 'active',
        'icon': 'fas fa-search-plus',
        'tool_path': '/osint/intel/holehe-pro/',
        'executable_name': 'python3',
        'command_template': 'python3 osint_tools/adapters/holehe_adapter.py {target}'
    }
]

added = 0
for tool_data in tools_to_add:
    tool, created = OSINTTool.objects.get_or_create(slug=tool_data['slug'], defaults=tool_data)
    if created:
        print(f"Created: {tool.name}")
        added += 1
    else:
        for key, value in tool_data.items():
            setattr(tool, key, value)
        tool.save()
        print(f"Updated: {tool.name}")

print(f"Successfully processed {len(tools_to_add)} external tools.")
