"""
GHunt Scraper - استخراج معلومات حسابات Google
يستخدم APIs عامة للحصول على معلومات عن حسابات Gmail
"""

import re
import json
import logging
import urllib.request
import urllib.parse
import ssl

logger = logging.getLogger(__name__)


class GHuntScraper:
    """
    Scraper لجمع معلومات عن حسابات Google/Gmail
    يستخدم APIs عامة ومتاحة بدون مفاتيح
    """
    
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        
    def investigate_email(self, email):
        """
        التحقيق في عنوان بريد Gmail
        
        Args:
            email: عنوان البريد الإلكتروني
            
        Returns:
            dict: معلومات الحساب
        """
        if not email or '@' not in email:
            return {
                'success': False,
                'error': 'عنوان بريد إلكتروني غير صالح',
                'email': email
            }
        
        # التحقق من أن البريد من Gmail
        domain = email.split('@')[1].lower()
        if domain not in ['gmail.com', 'googlemail.com']:
            return {
                'success': False,
                'error': 'هذه الأداة تعمل فقط مع حسابات Gmail',
                'email': email,
                'domain': domain
            }
        
        results = {
            'success': True,
            'email': email,
            'checks': {},
            'data': {}
        }
        
        # 1. التحقق من وجود الحساب عبر Google Calendar
        calendar_check = self._check_google_calendar(email)
        results['checks']['calendar'] = calendar_check
        
        # 2. التحقق من Google Photos
        photos_check = self._check_google_photos(email)
        results['checks']['photos'] = photos_check
        
        # 3. التحقق من Google Maps Reviews
        maps_check = self._check_google_maps(email)
        results['checks']['maps'] = maps_check
        
        # 4. استخراج معلومات من Google+/Profile (إن وجد)
        profile_info = self._get_profile_info(email)
        if profile_info:
            results['data']['profile'] = profile_info
        
        # 5. التحقق من YouTube
        youtube_check = self._check_youtube(email)
        results['checks']['youtube'] = youtube_check
        
        # تجميع النتائج
        results['summary'] = self._generate_summary(results)
        
        return results
    
    def _check_google_calendar(self, email):
        """التحقق من وجود Google Calendar عام"""
        try:
            # محاولة الوصول إلى Calendar API العام
            calendar_url = f'https://calendar.google.com/calendar/embed?src={urllib.parse.quote(email)}'
            
            req = urllib.request.Request(calendar_url)
            req.add_header('User-Agent', self.user_agent)
            
            ctx = ssl.create_default_context()
            with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
                content = response.read().decode('utf-8', errors='ignore')
                
                # التحقق من وجود محتوى التقويم
                if 'calendar' in content.lower() and 'google' in content.lower():
                    return {
                        'status': 'exists',
                        'public': True,
                        'url': calendar_url,
                        'message': 'تم العثور على تقويم Google عام'
                    }
                else:
                    return {
                        'status': 'private_or_not_found',
                        'public': False,
                        'message': 'التقويم خاص أو غير موجود'
                    }
                    
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {
                    'status': 'not_found',
                    'message': 'لا يوجد تقويم عام'
                }
            else:
                return {
                    'status': 'error',
                    'message': f'خطأ في الفحص: {e.code}'
                }
        except Exception as e:
            logger.error(f'خطأ في فحص Calendar: {e}')
            return {
                'status': 'error',
                'message': 'فشل الفحص'
            }
    
    def _check_google_photos(self, email):
        """التحقق من وجود ألبومات Google Photos عامة"""
        try:
            # محاولة الوصول إلى صفحة الملف الشخصي
            # Google Photos لا يوفر API عام مباشر، لكن يمكن التحقق من الوجود
            
            return {
                'status': 'limited_access',
                'message': 'Google Photos يتطلب مصادقة للوصول الكامل',
                'note': 'يمكن فقط رؤية الألبومات المشاركة علناً'
            }
            
        except Exception as e:
            logger.error(f'خطأ في فحص Photos: {e}')
            return {
                'status': 'error',
                'message': 'فشل الفحص'
            }
    
    def _check_google_maps(self, email):
        """التحقق من مراجعات Google Maps"""
        try:
            # Google Maps Reviews تتطلب Gaia ID
            # هذا فحص محدود بدون API key
            
            return {
                'status': 'limited_access',
                'message': 'مراجعات Google Maps تتطلب معرف Gaia ID',
                'note': 'يمكن البحث يدوياً عن المراجعات العامة'
            }
            
        except Exception as e:
            logger.error(f'خطأ في فحص Maps: {e}')
            return {
                'status': 'error',
                'message': 'فشل الفحص'
            }
    
    def _get_profile_info(self, email):
        """محاولة الحصول على معلومات الملف الشخصي"""
        try:
            # Google+ تم إيقافه، لكن بعض المعلومات قد تكون متاحة
            # عبر خدمات Google الأخرى
            
            username = email.split('@')[0]
            
            return {
                'username': username,
                'email': email,
                'note': 'معلومات الملف الشخصي محدودة بدون مصادقة'
            }
            
        except Exception as e:
            logger.error(f'خطأ في جلب Profile: {e}')
            return None
    
    def _check_youtube(self, email):
        """التحقق من وجود قناة YouTube مرتبطة"""
        try:
            # YouTube API يتطلب API key للبحث الكامل
            # لكن يمكن محاولة البحث العام
            
            username = email.split('@')[0]
            search_url = f'https://www.youtube.com/results?search_query={urllib.parse.quote(username)}'
            
            return {
                'status': 'search_available',
                'search_url': search_url,
                'message': 'يمكن البحث يدوياً عن القناة',
                'note': 'YouTube API يتطلب مفتاح للبحث الآلي'
            }
            
        except Exception as e:
            logger.error(f'خطأ في فحص YouTube: {e}')
            return {
                'status': 'error',
                'message': 'فشل الفحص'
            }
    
    def _generate_summary(self, results):
        """توليد ملخص النتائج"""
        summary = {
            'email': results['email'],
            'total_checks': len(results['checks']),
            'findings': []
        }
        
        for service, check in results['checks'].items():
            status = check.get('status', 'unknown')
            if status in ['exists', 'public', 'found']:
                summary['findings'].append(f'{service}: موجود')
            elif status == 'limited_access':
                summary['findings'].append(f'{service}: وصول محدود')
        
        if not summary['findings']:
            summary['findings'].append('لم يتم العثور على معلومات عامة')
        
        return summary


def main():
    """اختبار الـ scraper"""
    scraper = GHuntScraper()
    
    # اختبار مع بريد Gmail
    test_email = 'test@gmail.com'
    results = scraper.investigate_email(test_email)
    
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
