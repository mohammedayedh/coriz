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
        'name': 'CheckNames Domain OSINT',
        'slug': 'checknames-pro',
        'description': 'التحقق من توفر وحالة أسماء النطاقات (Domains) عبر 21 امتداد عالمي.',
        'tool_type': 'domain',
        'required_clearance': 'L1',
        'status': 'active',
        'icon': 'fas fa-globe',
        'tool_path': '/osint/intel/checknames-pro/',
        'executable_name': 'python3',
        'command_template': 'python3 osint_tools/adapters/checknames_adapter.py {target}'
    },
    {
        'name': 'EmailRep Reputation Analysis',
        'slug': 'emailrep-pro',
        'description': 'فحص سمعة البريد الإلكتروني وكشف الأنشطة المشبوهة، الحسابات المؤقتة، والتسريبات الموثقة.',
        'tool_type': 'email',
        'required_clearance': 'L1',
        'status': 'active',
        'icon': 'fas fa-envelope-open-text',
        'tool_path': '/osint/intel/emailrep-pro/',
        'executable_name': 'python3',
        'command_template': 'python3 osint_tools/adapters/emailrep_adapter.py {target}'
    },
    {
        'name': 'ViewDNS Ultimate Toolkit',
        'slug': 'viewdns-pro',
        'description': 'ترسانة مكونة من 14 أداة استخباراتية لتحليل النطاقات، والبحث العكسي عن الـ IP، وفحص الجدار الناري.',
        'tool_type': 'domain',
        'required_clearance': 'L2',
        'status': 'active',
        'icon': 'fas fa-shield-alt',
        'tool_path': '/osint/intel/viewdns-pro/',
        'executable_name': 'python3',
        'command_template': 'python3 osint_tools/adapters/viewdns_adapter.py {target}'
    },
    {
        'name': 'LeakPeek Data Breach',
        'slug': 'leakpeak-pro',
        'description': 'استخراج كلمات المرور والبيانات المسربة للبريد الإلكتروني من قواعد البيانات العميقة عبر LeakPeek.',
        'tool_type': 'email',
        'required_clearance': 'L3',
        'status': 'active',
        'icon': 'fas fa-mask',
        'tool_path': '/osint/intel/leakpeak-pro/',
        'executable_name': 'python3',
        'command_template': 'python3 osint_tools/adapters/leakpeak_adapter.py {target}'
    },
    {
        'name': 'OverpassMap Geo-Intelligence',
        'slug': 'overpassmap-pro',
        'description': 'استخبارات جغرافية: تحديد أماكن الارتكاز الحساسة مثل (المستشفيات، الشرطة، القواعد العسكرية، أبراج الاتصالات) داخل أي مدينة.',
        'tool_type': 'ip', # نستخدم ip أو location إن وجد
        'required_clearance': 'L2',
        'status': 'active',
        'icon': 'fas fa-map-marked-alt',
        'tool_path': '/osint/intel/overpassmap-pro/',
        'executable_name': 'python3',
        'command_template': 'python3 osint_tools/adapters/overpassmap_adapter.py {target}'
    },
    {
        'name': 'CVE-Stalker Vulnerabilities',
        'slug': 'cvestalker-pro',
        'description': 'البحث عن الثغرات الأمنية المكتشفة عالمياً للشركات أو الأنظمة بناءً على رقم الثغرة أو اسم النظام.',
        'tool_type': 'domain',
        'required_clearance': 'L1',
        'status': 'active',
        'icon': 'fas fa-bug',
        'tool_path': '/osint/intel/cvestalker-pro/',
        'executable_name': 'python3',
        'command_template': 'python3 osint_tools/adapters/cvestalker_adapter.py {target}'
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

print(f"Successfully processed {len(tools_to_add)} additional tools.")
