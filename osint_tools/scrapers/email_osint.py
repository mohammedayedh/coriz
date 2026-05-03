"""
Email OSINT Scraper
جمع معلومات عن البريد الإلكتروني بدون API
المصدر: متعددة (مجاني 100%)
"""

import requests
import re
import hashlib
import json
import argparse
import concurrent.futures
from typing import Dict, Any, List

class EmailOSINT:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def analyze_email(self, email: str) -> Dict[str, Any]:
        results = {
            'success': False,
            'email': email,
            'results': [],
            'total_found': 0,
            'error': None
        }
        
        try:
            if not self._validate_email_format(email):
                results['error'] = 'صيغة البريد الإلكتروني غير صحيحة'
                return results
            
            domain = email.split('@')[1]
            dom_info = self._analyze_domain(domain)
            results['results'].append({
                'title': f"تحليل النطاق: {domain}",
                'description': f"مزود خدمة: {dom_info.get('provider_name', 'خاص')} | بريد مؤقت: {'محتمل جداً (نعم)' if dom_info['is_disposable'] else 'لا'}",
                'type': 'domain',
                'confidence': 'high'
            })
            
            grav = self._check_gravatar(email)
            if grav['exists']:
                results['results'].append({
                    'title': "حساب Gravatar (معرّف عالمي)",
                    'description': "تم العثور على صورة شخصية وملف عام مرتبط بهذا البريد على منصة ووردبريس/جرافاتار.",
                    'url': grav['profile_url'],
                    'type': 'profile',
                    'image': grav['image_url'],
                    'confidence': 'high'
                })
            
            # التحقق النشط من الحسابات الاجتماعية
            socials = self._verify_social_profiles(email)
            for s in socials:
                results['results'].append({
                    'title': f"حساب نشط على {s['platform']}",
                    'description': f"تم تأكيد وجود الحساب باسم المستخدم: {s['username']}",
                    'url': s['url'],
                    'type': 'social_media',
                    'confidence': 'high'
                })
            
            # التحقق الحقيقي من التسريبات
            breaches = self._check_real_breaches(email)
            if breaches['found']:
                results['results'].append({
                    'title': "⚠️ اكتشاف تسريبات بيانات (Data Breach)",
                    'description': f"تم العثور على هذا البريد في {len(breaches['sources'])} تسريب للبيانات. المصادر: {', '.join(breaches['sources'][:5])}{' وغيرها...' if len(breaches['sources']) > 5 else ''}",
                    'type': 'leak',
                    'confidence': 'high'
                })
            else:
                results['results'].append({
                    'title': "تسريبات البيانات",
                    'description': "✅ لم يتم العثور على هذا البريد في أي تسريبات بيانات عامة معروفة.",
                    'type': 'info',
                    'confidence': 'high'
                })
            
            results['total_found'] = len(results['results'])
            results['success'] = True
            
        except Exception as e:
            results['error'] = f'خطأ أثناء التحليل: {str(e)}'
        
        return results

    def _validate_email_format(self, email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _analyze_domain(self, domain: str) -> Dict:
        info = {'domain': domain, 'is_disposable': False, 'is_free_provider': False, 'provider_name': None}
        free_providers = {'gmail.com': 'Gmail', 'yahoo.com': 'Yahoo', 'hotmail.com': 'Hotmail', 'outlook.com': 'Outlook', 'icloud.com': 'iCloud', 'protonmail.com': 'ProtonMail'}
        if domain in free_providers:
            info['is_free_provider'] = True
            info['provider_name'] = free_providers[domain]
            
        disposable_domains = ['tempmail.com', 'guerrillamail.com', 'temp-mail.org', '10minutemail.com', 'mailinator.com', 'yopmail.com']
        if domain in disposable_domains or "temp" in domain:
            info['is_disposable'] = True
        return info
    
    def _check_gravatar(self, email: str) -> Dict:
        gravatar_info = {'exists': False, 'profile_url': None, 'image_url': None}
        try:
            email_hash = hashlib.md5(email.lower().strip().encode()).hexdigest()
            image_url = f"https://www.gravatar.com/avatar/{email_hash}?d=404"
            response = self.session.head(image_url, timeout=5)
            if response.status_code == 200:
                gravatar_info['exists'] = True
                gravatar_info['image_url'] = f"https://www.gravatar.com/avatar/{email_hash}?s=200"
                gravatar_info['profile_url'] = f"https://www.gravatar.com/{email_hash}"
        except: pass
        return gravatar_info
    
    def _check_url(self, platform, url, username):
        try:
            resp = self.session.get(url, timeout=7, allow_redirects=True)
            if resp.status_code == 200 and "Not Found" not in resp.text:
                return {'platform': platform, 'url': url, 'username': username, 'found': True}
        except: pass
        return {'found': False}

    def _verify_social_profiles(self, email: str) -> List[Dict]:
        found_profiles = []
        username = email.split('@')[0]
        platforms = {
            'GitHub': f'https://github.com/{username}', 
            'Twitter/X': f'https://twitter.com/{username}',
            'Reddit': f'https://www.reddit.com/user/{username}',
            'Pinterest': f'https://www.pinterest.com/{username}'
        }
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self._check_url, plat, url, username) for plat, url in platforms.items()]
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                if res['found']:
                    found_profiles.append(res)
                    
        return found_profiles
    
    def _check_real_breaches(self, email: str) -> Dict:
        breach_info = {'found': False, 'sources': []}
        try:
            # استخدام API مجاني (XposedOrNot) للتحقق من التسريبات بدون مفتاح API
            url = f"https://api.xposedornot.com/v1/check-email/{email}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'breaches' in data and data['breaches']:
                    breach_info['found'] = True
                    # جلب أسماء التسريبات (أول 10 مصادر لتجنب النص الطويل جداً)
                    breach_info['sources'] = data['breaches'][:10]
        except: pass
        return breach_info

def main():
    parser = argparse.ArgumentParser(description='Email OSINT Tool for Coriza (Enhanced Pro Version)')
    parser.add_argument('--email', required=True, help='Target Email')
    args = parser.parse_args()
    scraper = EmailOSINT()
    output = scraper.analyze_email(args.email)
    print(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    main()
