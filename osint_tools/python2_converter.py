"""
محول بسيط لتحويل أدوات Python 2 إلى Python 3
"""
import os
import re
import shutil
from pathlib import Path


def convert_python2_to_python3(file_path):
    """تحويل ملف Python 2 إلى Python 3"""
    try:
        # قراءة الملف
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # إنشاء نسخة احتياطية
        backup_path = file_path + '.backup'
        shutil.copy2(file_path, backup_path)
        
        # التحويلات الأساسية
        # 1. تحويل print statements إلى print functions
        content = re.sub(r'\bprint\s+([^#\n]+)', r'print(\1)', content)
        
        # 2. إصلاح مشاكل أخرى شائعة
        content = content.replace('raw_input(', 'input(')
        content = content.replace('xrange(', 'range(')
        content = content.replace('unicode(', 'str(')
        
        # 3. إصلاح مشاكل الترميز
        content = content.replace('#!/usr/bin/env python', '#!/usr/bin/env python3')
        content = content.replace('#!/usr/bin/python', '#!/usr/bin/python3')
        
        # 4. إصلاح مشاكل regex
        content = re.sub(r'r"([^"]*\\[^"]*)"', r'r"\1"', content)
        content = re.sub(r"r'([^']*\\[^']*)'", r"r'\1'", content)
        
        # 5. إصلاح مشاكل الاستيراد
        content = content.replace('import urlparse', 'from urllib.parse import urlparse')
        content = content.replace('import urllib2', 'import urllib.request as urllib2')
        content = content.replace('import ConfigParser', 'import configparser as ConfigParser')
        content = content.replace('import HTMLParser', 'import html.parser as HTMLParser')
        content = content.replace('import httplib', 'import http.client as httplib')
        content = content.replace('import cookielib', 'import http.cookiejar as cookielib')
        
        # 6. إصلاح مشاكل أخرى
        content = content.replace('basestring', 'str')
        content = content.replace('iteritems()', 'items()')
        content = content.replace('itervalues()', 'values()')
        content = content.replace('iterkeys()', 'keys()')
        
        # كتابة الملف المحول
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"خطأ في تحويل الملف {file_path}: {e}")
        return False


def convert_tool_directory(tool_path):
    """تحويل جميع ملفات Python في مجلد الأداة"""
    converted_files = []
    
    for root, dirs, files in os.walk(tool_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if convert_python2_to_python3(file_path):
                    converted_files.append(file_path)
    
    return converted_files


if __name__ == "__main__":
    # تحويل أدوات محددة
    tools_to_convert = [
        'open_tool/Infoga-master',
        'open_tool/sherlock-master',
        'open_tool/GHunt-master',
        'open_tool/spiderfoot-master'
    ]
    
    for tool_path in tools_to_convert:
        if os.path.exists(tool_path):
            print(f"تحويل أداة: {tool_path}")
            converted = convert_tool_directory(tool_path)
            print(f"تم تحويل {len(converted)} ملف")
        else:
            print(f"المجلد غير موجود: {tool_path}")
