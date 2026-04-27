"""
ملف الأمان والحماية
"""

import hashlib
import secrets
import time
from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class SecurityUtils:
    """أدوات الأمان"""
    
    @staticmethod
    def generate_secure_token(length=32):
        """إنشاء رمز آمن"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_password(password, salt=None):
        """تشفير كلمة المرور"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # استخدام PBKDF2 للتشفير
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return key.hex(), salt
    
    @staticmethod
    def verify_password(password, hashed_password, salt):
        """التحقق من كلمة المرور"""
        key, _ = SecurityUtils.hash_password(password, salt)
        return key == hashed_password
    
    @staticmethod
    def sanitize_input(input_string):
        """تنظيف المدخلات"""
        if not input_string:
            return ""
        
        # إزالة الأحرف الخطيرة
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`', '$']
        for char in dangerous_chars:
            input_string = input_string.replace(char, '')
        
        return input_string.strip()
    
    @staticmethod
    def validate_email(email):
        """التحقق من صحة البريد الإلكتروني"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        """التحقق من صحة رقم الهاتف"""
        import re
        pattern = r'^(\+966|0)?[5-9][0-9]{8}$'
        return re.match(pattern, phone) is not None


class CSRFProtection:
    """حماية CSRF"""
    
    @staticmethod
    def generate_csrf_token():
        """إنشاء رمز CSRF"""
        token = secrets.token_urlsafe(32)
        cache.set(f"csrf_token_{token}", True, 3600)  # ساعة واحدة
        return token
    
    @staticmethod
    def verify_csrf_token(token):
        """التحقق من رمز CSRF"""
        return cache.get(f"csrf_token_{token}") is not None
    
    @staticmethod
    def invalidate_csrf_token(token):
        """إبطال رمز CSRF"""
        cache.delete(f"csrf_token_{token}")


class RateLimiter:
    """محدد المعدل"""
    
    @staticmethod
    def check_rate_limit(identifier, limit=100, window=3600):
        """فحص حد المعدل"""
        cache_key = f"rate_limit_{identifier}"
        current_count = cache.get(cache_key, 0)
        
        if current_count >= limit:
            return False
        
        cache.set(cache_key, current_count + 1, window)
        return True
    
    @staticmethod
    def get_remaining_requests(identifier, limit=100):
        """الحصول على عدد الطلبات المتبقية"""
        cache_key = f"rate_limit_{identifier}"
        current_count = cache.get(cache_key, 0)
        return max(0, limit - current_count)


class IPWhitelist:
    """قائمة IP المسموحة"""
    
    @staticmethod
    def is_allowed(ip_address):
        """فحص إذا كان IP مسموح"""
        allowed_ips = getattr(settings, 'ALLOWED_IPS', [])
        return ip_address in allowed_ips
    
    @staticmethod
    def is_blocked(ip_address):
        """فحص إذا كان IP محظور"""
        blocked_ips = getattr(settings, 'BLOCKED_IPS', [])
        return ip_address in blocked_ips


class SecurityHeaders:
    """رؤوس الأمان"""
    
    @staticmethod
    def get_security_headers():
        """الحصول على رؤوس الأمان"""
        return {
            'X-XSS-Protection': '1; mode=block',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-Permitted-Cross-Domain-Policies': 'none',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        }


class InputValidator:
    """التحقق من المدخلات"""
    
    @staticmethod
    def validate_string(value, min_length=1, max_length=255, allowed_chars=None):
        """التحقق من النص"""
        if not isinstance(value, str):
            return False
        
        if len(value) < min_length or len(value) > max_length:
            return False
        
        if allowed_chars:
            for char in value:
                if char not in allowed_chars:
                    return False
        
        return True
    
    @staticmethod
    def validate_number(value, min_value=None, max_value=None):
        """التحقق من الرقم"""
        try:
            num = float(value)
            if min_value is not None and num < min_value:
                return False
            if max_value is not None and num > max_value:
                return False
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_url(url):
        """التحقق من الرابط"""
        import re
        pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
        return re.match(pattern, url) is not None


class FileSecurity:
    """أمان الملفات"""
    
    ALLOWED_EXTENSIONS = {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
        'documents': ['.pdf', '.doc', '.docx', '.txt'],
        'archives': ['.zip', '.rar', '.7z']
    }
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    
    @staticmethod
    def is_allowed_file(filename, file_type='images'):
        """فحص إذا كان الملف مسموح"""
        import os
        ext = os.path.splitext(filename)[1].lower()
        return ext in FileSecurity.ALLOWED_EXTENSIONS.get(file_type, [])
    
    @staticmethod
    def is_safe_file_size(file_size):
        """فحص حجم الملف"""
        return file_size <= FileSecurity.MAX_FILE_SIZE
    
    @staticmethod
    def scan_file_for_malware(file_path):
        """فحص الملف للبرمجيات الخبيثة"""
        # هنا يمكن إضافة منطق فحص الملفات
        # مثل استخدام ClamAV أو خدمات أخرى
        return True


class SessionSecurity:
    """أمان الجلسات"""
    
    @staticmethod
    def generate_session_id():
        """إنشاء معرف جلسة آمن"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_session(session_id):
        """التحقق من صحة الجلسة"""
        # فحص الجلسة في قاعدة البيانات أو التخزين المؤقت
        return True
    
    @staticmethod
    def invalidate_session(session_id):
        """إبطال الجلسة"""
        # حذف الجلسة من قاعدة البيانات أو التخزين المؤقت
        pass


class AuditLogger:
    """مسجل التدقيق"""
    
    @staticmethod
    def log_security_event(event_type, user_id, ip_address, details):
        """تسجيل حدث أمني"""
        logger.warning(f"Security Event: {event_type} - User: {user_id} - IP: {ip_address} - Details: {details}")
    
    @staticmethod
    def log_authentication_attempt(username, ip_address, success):
        """تسجيل محاولة تسجيل الدخول"""
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"Authentication Attempt: {username} - IP: {ip_address} - Status: {status}")
    
    @staticmethod
    def log_file_upload(filename, user_id, ip_address, file_size):
        """تسجيل رفع الملف"""
        logger.info(f"File Upload: {filename} - User: {user_id} - IP: {ip_address} - Size: {file_size}")


class SecurityMiddleware(MiddlewareMixin):
    """وسيط الأمان الشامل"""
    
    def process_request(self, request):
        # فحص IP
        ip_address = self.get_client_ip(request)
        
        if IPWhitelist.is_blocked(ip_address):
            logger.warning(f"Blocked IP attempted access: {ip_address}")
            return HttpResponseForbidden("الوصول محظور")
        
        # فحص حد المعدل
        if not RateLimiter.check_rate_limit(ip_address):
            logger.warning(f"Rate limit exceeded for IP: {ip_address}")
            return HttpResponseForbidden("تم تجاوز حد الطلبات المسموح")
        
        return None
    
    def process_response(self, request, response):
        # إضافة رؤوس الأمان
        security_headers = SecurityHeaders.get_security_headers()
        for header, value in security_headers.items():
            response[header] = value
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

