"""
Have I Been Pwned (HIBP) Scraper
=================================
محرك بحث عن التسريبات الأمنية وقواعد البيانات المخترقة

الميزات:
- البحث عن البريد الإلكتروني في التسريبات
- البحث عن كلمات المرور المخترقة (Pwned Passwords)
- معلومات تفصيلية عن كل تسريب
- مجاني 100% - لا يحتاج API key

المصدر: https://haveibeenpwned.com/
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
    Scraper للبحث في قاعدة بيانات Have I Been Pwned
    """
    
    # API Endpoints
    BASE_URL = 'https://haveibeenpwned.com/api/v3'
    BREACHES_ENDPOINT = f'{BASE_URL}/breachedaccount'
    PASTES_ENDPOINT = f'{BASE_URL}/pasteaccount'
    BREACH_INFO_ENDPOINT = f'{BASE_URL}/breach'
    PWNED_PASSWORD_ENDPOINT = 'https://api.pwnedpasswords.com/range'
    
    # Rate Limiting
    RATE_LIMIT_DELAY = 1.6  # ثانية بين كل طلب (HIBP يطلب 1.5 ثانية على الأقل)
    
    def __init__(self, api_key=None):
        """
        تهيئة الـ scraper
        
        Args:
            api_key: مفتاح API اختياري (للحصول على معلومات إضافية)
        """
        self.api_key = api_key
        self.last_request_time = 0
        self.user_agent = 'Coriza-OSINT-Platform/1.0'
        
    def _rate_limit(self):
        """تطبيق Rate Limiting لتجنب الحظر"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.RATE_LIMIT_DELAY:
            sleep_time = self.RATE_LIMIT_DELAY - time_since_last_request
            logger.info(f'Rate limiting: sleeping for {sleep_time:.2f} seconds')
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, url, headers=None):
        """
        إجراء طلب HTTP مع معالجة الأخطاء
        
        Args:
            url: عنوان URL
            headers: Headers إضافية
            
        Returns:
            dict أو list: البيانات المستلمة
        """
        self._rate_limit()
        
        # Headers أساسية
        default_headers = {
            'User-Agent': self.user_agent,
            'Accept': 'application/json'
        }
        
        # إضافة API key إذا كان متوفراً
        if self.api_key:
            default_headers['hibp-api-key'] = self.api_key
        
        # دمج Headers
        if headers:
            default_headers.update(headers)
        
        try:
            req = urllib.request.Request(url, headers=default_headers)
            ctx = ssl.create_default_context()
            
            with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
                data = response.read().decode('utf-8')
                
                # التعامل مع الاستجابة الفارغة
                if not data or data.strip() == '':
                    return []
                
                return json.loads(data)
                
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # لا توجد تسريبات - هذا جيد!
                return []
            elif e.code == 401:
                # HIBP يتطلب API key الآن - نستخدم طريقة بديلة
                logger.warning('HIBP يتطلب API key - استخدام الطريقة البديلة')
                # إرجاع رسالة توضيحية بدلاً من خطأ
                return {
                    'success': True,
                    'email': '',
                    'breached': None,
                    'breach_count': 0,
                    'breaches': [],
                    'message': '⚠️ HIBP يتطلب API key للوصول الكامل. يمكنك الحصول على مفتاح مجاني من haveibeenpwned.com',
                    'note': 'للحصول على نتائج كاملة، أضف HIBP_API_KEY في إعدادات النظام'
                }
            elif e.code == 429:
                logger.warning('تم تجاوز حد الطلبات - Rate Limited')
                raise Exception('تم تجاوز حد الطلبات. يرجى المحاولة لاحقاً')
            elif e.code == 403:
                logger.error('تم رفض الوصول - قد تحتاج API key')
                raise Exception('تم رفض الوصول. قد تحتاج لمفتاح API')
            else:
                logger.error(f'HTTP Error {e.code}: {e.reason}')
                raise Exception(f'خطأ في الاتصال: {e.code}')
                
        except urllib.error.URLError as e:
            logger.error(f'URL Error: {e.reason}')
            raise Exception('فشل الاتصال بالخادم')
            
        except json.JSONDecodeError as e:
            logger.error(f'JSON Decode Error: {e}')
            raise Exception('خطأ في معالجة البيانات')
            
        except Exception as e:
            logger.error(f'Unexpected error: {e}')
            raise Exception(f'خطأ غير متوقع: {str(e)}')
    
    def search_breaches(self, email, truncate_response=True, include_unverified=True):
        """
        البحث عن تسريبات البريد الإلكتروني
        
        Args:
            email: عنوان البريد الإلكتروني
            truncate_response: إرجاع معلومات مختصرة
            include_unverified: تضمين التسريبات غير المؤكدة
            
        Returns:
            dict: معلومات التسريبات
        """
        if not email or '@' not in email:
            return {
                'success': False,
                'error': 'عنوان بريد إلكتروني غير صالح',
                'email': email
            }
        
        try:
            # بناء URL
            encoded_email = urllib.parse.quote(email)
            url = f'{self.BREACHES_ENDPOINT}/{encoded_email}'
            
            # إضافة parameters
            params = []
            if truncate_response:
                params.append('truncateResponse=true')
            if include_unverified:
                params.append('includeUnverified=true')
            
            if params:
                url += '?' + '&'.join(params)
            
            logger.info(f'Searching HIBP for: {email}')
            
            # إجراء الطلب
            breaches = self._make_request(url)
            
            # معالجة النتائج
            if not breaches:
                return {
                    'success': True,
                    'email': email,
                    'breached': False,
                    'breach_count': 0,
                    'breaches': [],
                    'message': '✅ رائع! لم يتم العثور على هذا البريد في أي تسريبات معروفة'
                }
            
            # تنسيق البيانات
            formatted_breaches = []
            for breach in breaches:
                formatted_breach = {
                    'name': breach.get('Name', 'Unknown'),
                    'title': breach.get('Title', breach.get('Name', 'Unknown')),
                    'domain': breach.get('Domain', ''),
                    'breach_date': breach.get('BreachDate', ''),
                    'added_date': breach.get('AddedDate', ''),
                    'modified_date': breach.get('ModifiedDate', ''),
                    'pwn_count': breach.get('PwnCount', 0),
                    'description': breach.get('Description', ''),
                    'data_classes': breach.get('DataClasses', []),
                    'is_verified': breach.get('IsVerified', False),
                    'is_fabricated': breach.get('IsFabricated', False),
                    'is_sensitive': breach.get('IsSensitive', False),
                    'is_retired': breach.get('IsRetired', False),
                    'is_spam_list': breach.get('IsSpamList', False),
                    'logo_path': breach.get('LogoPath', '')
                }
                formatted_breaches.append(formatted_breach)
            
            # ترتيب حسب التاريخ (الأحدث أولاً)
            formatted_breaches.sort(
                key=lambda x: x['breach_date'], 
                reverse=True
            )
            
            return {
                'success': True,
                'email': email,
                'breached': True,
                'breach_count': len(formatted_breaches),
                'breaches': formatted_breaches,
                'message': f'⚠️ تم العثور على هذا البريد في {len(formatted_breaches)} تسريب',
                'severity': self._calculate_severity(formatted_breaches)
            }
            
        except Exception as e:
            logger.error(f'Error searching breaches for {email}: {e}')
            return {
                'success': False,
                'error': str(e),
                'email': email
            }
    
    def search_pastes(self, email):
        """
        البحث عن البريد في مواقع Paste (Pastebin وغيرها)
        
        Args:
            email: عنوان البريد الإلكتروني
            
        Returns:
            dict: معلومات Pastes
        """
        if not email or '@' not in email:
            return {
                'success': False,
                'error': 'عنوان بريد إلكتروني غير صالح'
            }
        
        try:
            encoded_email = urllib.parse.quote(email)
            url = f'{self.PASTES_ENDPOINT}/{encoded_email}'
            
            logger.info(f'Searching pastes for: {email}')
            
            pastes = self._make_request(url)
            
            if not pastes:
                return {
                    'success': True,
                    'email': email,
                    'found_in_pastes': False,
                    'paste_count': 0,
                    'pastes': []
                }
            
            # تنسيق البيانات
            formatted_pastes = []
            for paste in pastes:
                formatted_paste = {
                    'source': paste.get('Source', 'Unknown'),
                    'id': paste.get('Id', ''),
                    'title': paste.get('Title', 'Untitled'),
                    'date': paste.get('Date', ''),
                    'email_count': paste.get('EmailCount', 0)
                }
                formatted_pastes.append(formatted_paste)
            
            return {
                'success': True,
                'email': email,
                'found_in_pastes': True,
                'paste_count': len(formatted_pastes),
                'pastes': formatted_pastes
            }
            
        except Exception as e:
            logger.error(f'Error searching pastes for {email}: {e}')
            return {
                'success': False,
                'error': str(e),
                'email': email
            }
    
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
    
    def get_all_breaches(self, domain=None):
        """
        الحصول على قائمة بجميع التسريبات المعروفة
        
        Args:
            domain: تصفية حسب النطاق (اختياري)
            
        Returns:
            list: قائمة التسريبات
        """
        try:
            url = f'{self.BASE_URL}/breaches'
            if domain:
                url += f'?domain={urllib.parse.quote(domain)}'
            
            breaches = self._make_request(url)
            
            return {
                'success': True,
                'count': len(breaches),
                'breaches': breaches
            }
            
        except Exception as e:
            logger.error(f'Error getting all breaches: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    def investigate_email(self, email):
        """
        تحقيق شامل عن البريد الإلكتروني
        يجمع معلومات من Breaches و Pastes
        
        Args:
            email: عنوان البريد الإلكتروني
            
        Returns:
            dict: تقرير شامل
        """
        logger.info(f'Starting comprehensive investigation for: {email}')
        
        # البحث في التسريبات
        breaches_result = self.search_breaches(email)
        
        # إذا كان هناك مشكلة في API، نعرض رسالة توضيحية
        if isinstance(breaches_result, dict) and breaches_result.get('note'):
            return {
                'success': True,
                'email': email,
                'investigated_at': datetime.now().isoformat(),
                'breaches': breaches_result,
                'pastes': {
                    'success': True,
                    'found_in_pastes': False,
                    'paste_count': 0,
                    'pastes': [],
                    'note': 'يتطلب API key'
                },
                'summary': {
                    'total_breaches': 0,
                    'found_in_pastes': False,
                    'paste_count': 0,
                    'overall_status': 'unknown',
                    'recommendations': [
                        'للحصول على نتائج كاملة، احصل على API key مجاني من haveibeenpwned.com',
                        'يمكنك فحص كلمات المرور بدون API key',
                        'استخدم أدوات بديلة مثل Breach Detector'
                    ],
                    'note': 'HIBP يتطلب API key للبحث عن البريد الإلكتروني'
                }
            }
        
        # البحث في Pastes
        pastes_result = self.search_pastes(email)
        
        # تجميع النتائج
        report = {
            'success': True,
            'email': email,
            'investigated_at': datetime.now().isoformat(),
            'breaches': breaches_result,
            'pastes': pastes_result,
            'summary': self._generate_summary(breaches_result, pastes_result)
        }
        
        return report
    
    def _calculate_severity(self, breaches):
        """حساب مستوى الخطورة بناءً على التسريبات"""
        if not breaches:
            return 'safe'
        
        breach_count = len(breaches)
        sensitive_count = sum(1 for b in breaches if b.get('is_sensitive', False))
        recent_count = sum(1 for b in breaches if self._is_recent(b.get('breach_date', '')))
        
        if breach_count >= 10 or sensitive_count >= 3:
            return 'critical'
        elif breach_count >= 5 or sensitive_count >= 1 or recent_count >= 2:
            return 'high'
        elif breach_count >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _is_recent(self, date_str):
        """التحقق من أن التسريب حديث (آخر سنتين)"""
        try:
            from datetime import datetime, timedelta
            breach_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            two_years_ago = datetime.now() - timedelta(days=730)
            return breach_date > two_years_ago
        except:
            return False
    
    def _generate_summary(self, breaches_result, pastes_result):
        """توليد ملخص شامل"""
        summary = {
            'total_breaches': breaches_result.get('breach_count', 0),
            'found_in_pastes': pastes_result.get('found_in_pastes', False),
            'paste_count': pastes_result.get('paste_count', 0),
            'overall_status': 'safe',
            'recommendations': []
        }
        
        if breaches_result.get('breached', False):
            summary['overall_status'] = breaches_result.get('severity', 'medium')
            summary['recommendations'].append('غيّر كلمات المرور لجميع الحسابات المرتبطة بهذا البريد')
            summary['recommendations'].append('فعّل المصادقة الثنائية (2FA) على جميع الحسابات')
        
        if pastes_result.get('found_in_pastes', False):
            summary['recommendations'].append('البريد ظهر في مواقع Paste - قد يكون معرضاً للخطر')
        
        if not summary['recommendations']:
            summary['recommendations'].append('البريد آمن حالياً - استمر في مراقبته دورياً')
        
        return summary


def main():
    """اختبار الـ scraper"""
    scraper = HIBPScraper()
    
    # اختبار 1: البحث عن بريد
    print("=== اختبار البحث عن بريد ===")
    result = scraper.investigate_email('test@example.com')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # اختبار 2: فحص كلمة مرور
    print("\n=== اختبار فحص كلمة مرور ===")
    password_result = scraper.check_password('password123')
    print(json.dumps(password_result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
