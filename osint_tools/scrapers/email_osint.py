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
                'description': f"مزود خدمة: {dom_info.get('provider_name', 'خاص')} | بريد مؤقت: {'نعم' if dom_info['is_disposable'] else 'لا'}",
                'type': 'domain',
                'confidence': 'high'
            })
            
            grav = self._check_gravatar(email)
            if grav['exists']:
                results['results'].append({
                    'title': "حساب Gravatar مكتشف",
                    'description': "تم العثور على صورة شخصية وملف عام مرتبط بهذا البريد.",
                    'url': grav['profile_url'],
                    'type': 'profile',
                    'image': grav['image_url'],
                    'confidence': 'high'
                })
            
            socials = self._find_social_profiles(email)
            for s in socials:
                results['results'].append({
                    'title': f"ملف محتمل على {s['platform']}",
                    'description': f"اسم المستخدم المتوقع: {s['username']} (يتطلب تحقق يدوي)",
                    'url': s['possible_url'],
                    'type': 'social_media',
                    'confidence': 'medium'
                })
            
            breach = self._check_breaches_limited(email)
            results['results'].append({
                'title': "توصيات الأمان الاستباقية",
                'description': " • ".join(breach['recommendations']),
                'type': 'other',
                'confidence': 'unknown'
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
        free_providers = {'gmail.com': 'Gmail', 'yahoo.com': 'Yahoo', 'hotmail.com': 'Hotmail', 'outlook.com': 'Outlook'}
        if domain in free_providers:
            info['is_free_provider'] = True
            info['provider_name'] = free_providers[domain]
        disposable_domains = ['tempmail.com', 'guerrillamail.com', 'temp-mail.org']
        if domain in disposable_domains:
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
                gravatar_info['image_url'] = f"https://www.gravatar.com/avatar/{email_hash}"
                gravatar_info['profile_url'] = f"https://www.gravatar.com/{email_hash}"
        except: pass
        return gravatar_info
    
    def _find_social_profiles(self, email: str) -> List[Dict]:
        profiles = []
        username = email.split('@')[0]
        platforms = {'GitHub': f'https://github.com/{username}', 'Twitter': f'https://twitter.com/{username}'}
        for platform, url in platforms.items():
            profiles.append({'platform': platform, 'possible_url': url, 'username': username})
        return profiles
    
    def _check_breaches_limited(self, email: str) -> Dict:
        return {'recommendations': ['استخدم كلمات مرور قوية', 'فعّل المصادقة الثنائية']}

def main():
    parser = argparse.ArgumentParser(description='Email OSINT Tool for Coriza')
    parser.add_argument('--email', required=True, help='Target Email')
    args = parser.parse_args()
    scraper = EmailOSINT()
    output = scraper.analyze_email(args.email)
    print(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    main()
