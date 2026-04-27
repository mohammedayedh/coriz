import os
import django
import sys

# إعداد بيئة Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coriza.settings')
django.setup()

from osint_tools.models import OSINTTool

def register_tools():
    tools = [
        {
            "name": "CVE-Stalker Vulnerabilities",
            "slug": "cvestalker-pro",
            "description": "Advanced vulnerability intelligence scanner using CVE-Stalker API.",
            "tool_type": "domain",
            "source_type": "private",
            "command_template": "python3 osint_tools/adapters/cvestalker_adapter.py \"{target}\"",
            "required_clearance": "L2",
            "timeout": 60,
            "is_active": True
        },
        {
            "name": "MxToolbox Intelligence",
            "slug": "mxtoolbox-pro",
            "description": "Comprehensive DNS, MX, and Blacklist analysis via MxToolbox API.",
            "tool_type": "domain",
            "source_type": "private",
            "command_template": "python3 osint_tools/adapters/mxtoolbox_adapter.py \"{target}\" --command a",
            "required_clearance": "L2",
            "timeout": 60,
            "is_active": True
        },
        {
            "name": "ViewDNS Ultimate Toolkit",
            "slug": "viewdns-pro",
            "description": "Deep domain and IP intelligence toolkit using ViewDNS API.",
            "tool_type": "domain",
            "source_type": "private",
            "command_template": "python3 osint_tools/adapters/viewdns_adapter.py \"{target}\" --command dnsrecord",
            "required_clearance": "L2",
            "timeout": 60,
            "is_active": True
        },
        {
            "name": "Hudson Rock Infostealer Search",
            "slug": "hudsonrock-pro",
            "description": "Search for compromised records in Hudson Rock's infostealer database.",
            "tool_type": "email",
            "source_type": "leaked",
            "command_template": "python3 osint_tools/adapters/hudsonrock_adapter.py \"{target}\" --type 1",
            "required_clearance": "L3",
            "timeout": 60,
            "is_active": True
        },
        {
            "name": "Holehe Accounts OSINT",
            "slug": "holehe-pro",
            "description": "Deeply analyze email usage across 120+ platforms to find linked accounts.",
            "tool_type": "email",
            "source_type": "open",
            "command_template": "python3 osint_tools/adapters/holehe_adapter.py \"{target}\"",
            "required_clearance": "L2",
            "timeout": 120,
            "is_active": True
        },
        {
            "name": "Reverse Image Intelligence",
            "slug": "reverse-image",
            "description": "Cross-search images across Google, Yandex, Bing, and TinEye.",
            "tool_type": "general",
            "source_type": "open",
            "command_template": "python3 osint_tools/scrapers/reverse_image.py --url \"{target}\"",
            "required_clearance": "L1",
            "timeout": 30,
            "is_active": True
        }
    ]

    for tool_data in tools:
        tool, created = OSINTTool.objects.update_or_create(
            slug=tool_data['slug'],
            defaults=tool_data
        )
        if created:
            print(f"Created tool: {tool.name}")
        else:
            print(f"Updated tool: {tool.name}")

if __name__ == "__main__":
    register_tools()
