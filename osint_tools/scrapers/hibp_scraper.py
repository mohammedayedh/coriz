"""
Have I Been Pwned (HIBP) - Password Checker
============================================
فحص كلمات المرور في قاعدة بيانات التسريبات

الميزات:
- فحص كلمات المرور المخترقة (Pwned Passwords)
- يستخدم k-Anonymity - لا يرسل كلمة المرور كاملة
- مجاني 100% - لا يحتاج API key
- أكثر من 850 مليون كلمة مرور مخترقة

المصدر: https://haveibeenpwned.com/Passwords
المطور: Troy Hunt
"""

import json
import logging
import urllib.request
import urllib.parse
import urllib.error
import ssl
import time
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)


class HIBPScraper:
    """
    Scraper لفحص كلمات المرور في قاعدة بيانات Have I Been Pwned
    يعمل بدون API key - مجاني 100%
    """
    
    # API Endpoint لفحص كلمات المرور (مجاني بدون API key)
    PWNED_PASSWORD_ENDPOINT = 'https://api.pwnedpasswords.com/range'
    
    def __init__(self):
        """تهيئة الـ scraper"""
        self.user_agent = 'Coriza-OSINT-Platform/1.0'
        

    

    
    def check_password(self, password):
        """
        التحقق من كلمة المرور في قاعدة بيانات Pwned Passwords
        يستخدم k-Anonymity - لا يرسل كلمة المرور كاملة
        
        Args:
            password: كلمة المرور للفحص
            
        Returns:
            dict: معلومات عن كلمة المرور
        """
        if not password:
            return {
                'success': False,
                'error': 'كلمة المرور فارغة'
            }
        
        try:
            # حساب SHA-1 hash
            sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
            
            # استخدام k-Anonymity: إرسال أول 5 أحرف فقط
            prefix = sha1_hash[:5]
            suffix = sha1_hash[5:]
            
            url = f'{self.PWNED_PASSWORD_ENDPOINT}/{prefix}'
            
            logger.info(f'Checking password hash prefix: {prefix}')
            
            # إجراء الطلب (بدون rate limiting لأن هذا API مختلف)
            req = urllib.request.Request(url, headers={'User-Agent': self.user_agent})
            ctx = ssl.create_default_context()
            
            with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
                data = response.read().decode('utf-8')
            
            # البحث عن الـ suffix في النتائج
            for line in data.split('\n'):
                if ':' in line:
                    hash_suffix, count = line.split(':')
                    if hash_suffix.strip() == suffix:
                        count = int(count.strip())
                        return {
                            'success': True,
                            'pwned': True,
                            'count': count,
                            'message': f'⚠️ كلمة المرور هذه ظهرت في {count:,} تسريب!',
                            'severity': 'critical' if count > 100000 else 'high' if count > 10000 else 'medium'
                        }
            
            # كلمة المرور آمنة
            return {
                'success': True,
                'pwned': False,
                'count': 0,
                'message': '✅ كلمة المرور آمنة - لم تظهر في أي تسريبات معروفة',
                'severity': 'safe'
            }
            
        except Exception as e:
            logger.error(f'Error checking password: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    

    
    def investigate_email(self, password_input):
        """
        فحص كلمة مرور في قاعدة بيانات HIBP
        
        Args:
            password_input: كلمة المرور للفحص
            
        Returns:
            dict: نتيجة الفحص
        """
        # التحقق من المدخل
        if not password_input or not password_input.strip():
            return {
                'success': False,
                'error': 'كلمة المرور فارغة',
                'type': 'password_check'
            }
        
        password_input = password_input.strip()
        
        # فحص كلمة المرور
        logger.info(f'Password check for: {password_input[:3]}***')
        password_result = self.check_password(password_input)
        
        return {
            'success': True,
            'type': 'password_check',
            'input': password_input[:3] + '***',  # إخفاء كلمة المرور
            'investigated_at': datetime.now().isoformat(),
            'password_check': password_result,
            'summary': {
                'check_type': 'password',
                'pwned': password_result.get('pwned', False),
                'count': password_result.get('count', 0),
                'severity': password_result.get('severity', 'unknown'),
                'recommendations': self._get_password_recommendations(password_result)
            }
        }
    
    def _get_password_recommendations(self, password_result):
        """توليد توصيات بناءً على نتيجة فحص كلمة المرور"""
        if not password_result.get('success'):
            return ['حدث خطأ في فحص كلمة المرور']
        
        if password_result.get('pwned'):
            count = password_result.get('count', 0)
            severity = password_result.get('severity', 'unknown')
            
            recommendations = [
                f'⚠️ كلمة المرور هذه ظهرت في {count:,} تسريب!',
                '🔴 لا تستخدم هذه الكلمة أبداً',
                '✅ استخدم كلمة مرور قوية وفريدة',
                '✅ استخدم مدير كلمات مرور',
                '✅ فعّل المصادقة الثنائية (2FA)'
            ]
            
            if severity == 'critical':
                recommendations.insert(1, '🚨 خطر شديد: هذه من أكثر كلمات المرور شيوعاً!')
            
            return recommendations
        else:
            return [
                '✅ كلمة المرور آمنة - لم تظهر في أي تسريبات معروفة',
                '💡 استمر في استخدام كلمات مرور قوية وفريدة',
                '💡 فعّل المصادقة الثنائية للحماية الإضافية'
            ]
    



def main():
    """اختبار الـ scraper"""
    scraper = HIBPScraper()
    
    # اختبار فحص كلمات مرور
    print("=== اختبار فحص كلمات مرور ===")
    
    passwords = ['password123', '123456', 'MyS3cur3P@ssw0rd!2024']
    
    for pwd in passwords:
        print(f"\n--- فحص: {pwd[:3]}*** ---")
        result = scraper.investigate_email(pwd)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
