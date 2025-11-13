from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SecurityMiddleware(MiddlewareMixin):
    """وسيط الأمان"""
    
    def process_request(self, request):
        # إضافة رؤوس الأمان
        response = None
        
        # منع XSS
        if hasattr(settings, 'SECURE_BROWSER_XSS_FILTER') and settings.SECURE_BROWSER_XSS_FILTER:
            response = response or HttpResponseForbidden()
            response['X-XSS-Protection'] = '1; mode=block'
        
        # منع MIME sniffing
        if hasattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF') and settings.SECURE_CONTENT_TYPE_NOSNIFF:
            response = response or HttpResponseForbidden()
            response['X-Content-Type-Options'] = 'nosniff'
        
        # منع clickjacking
        if hasattr(settings, 'X_FRAME_OPTIONS'):
            response = response or HttpResponseForbidden()
            response['X-Frame-Options'] = settings.X_FRAME_OPTIONS
        
        # إضافة رؤوس أمان إضافية
        response = response or HttpResponseForbidden()
        response['X-Permitted-Cross-Domain-Policies'] = 'none'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """وسيط تحديد المعدل"""
    
    def process_request(self, request):
        # تحديد المعدل للطلبات
        if request.method in ['POST', 'PUT', 'DELETE']:
            ip_address = self.get_client_ip(request)
            cache_key = f"rate_limit_{ip_address}"
            
            # فحص المعدل
            request_count = cache.get(cache_key, 0)
            if request_count >= 100:  # 100 طلب في الساعة
                logger.warning(f"Rate limit exceeded for IP: {ip_address}")
                return HttpResponseForbidden("تم تجاوز حد الطلبات المسموح")
            
            # زيادة العداد
            cache.set(cache_key, request_count + 1, 3600)  # ساعة واحدة
        
        return None
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LoggingMiddleware(MiddlewareMixin):
    """وسيط التسجيل"""
    
    def process_request(self, request):
        # تسجيل الطلبات المهمة
        if request.method in ['POST', 'PUT', 'DELETE']:
            logger.info(f"{request.method} {request.path} - IP: {self.get_client_ip(request)}")
        
        return None
    
    def process_response(self, request, response):
        # تسجيل الاستجابات
        if response.status_code >= 400:
            logger.warning(f"{request.method} {request.path} - Status: {response.status_code}")
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class MaintenanceMiddleware(MiddlewareMixin):
    """وسيط وضع الصيانة"""
    
    def process_request(self, request):
        # فحص وضع الصيانة
        if hasattr(settings, 'MAINTENANCE_MODE') and settings.MAINTENANCE_MODE:
            # السماح للمديرين بالوصول
            if request.user.is_authenticated and request.user.is_staff:
                return None
            
            # منع الوصول للآخرين
            return HttpResponseForbidden("الموقع في وضع الصيانة")
        
        return None

