from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SecurityMiddleware(MiddlewareMixin):
    """وسيط الأمان — يُضيف Security Headers لكل استجابة."""

    # رؤوس ثابتة تُضاف لكل استجابة
    _SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Permitted-Cross-Domain-Policies': 'none',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
    }

    def process_request(self, request):
        # ✅ لا نُعيد شيئًا هنا — نُتيح للطلب المرور الكامل
        return None

    def process_response(self, request, response):
        """المكان الصحيح لإضافة Security Headers (على الاستجابة لا الطلب)."""
        for header, value in self._SECURITY_HEADERS.items():
            response.setdefault(header, value)

        # X-XSS-Protection (مفيد للمتصفحات القديمة)
        if getattr(settings, 'SECURE_BROWSER_XSS_FILTER', True):
            response.setdefault('X-XSS-Protection', '1; mode=block')

        # X-Frame-Options من الإعدادات
        x_frame = getattr(settings, 'X_FRAME_OPTIONS', 'DENY')
        response.setdefault('X-Frame-Options', x_frame)

        return response


class RateLimitMiddleware(MiddlewareMixin):
    """وسيط تحديد معدل الطلبات لمنع الإساءة."""

    _LIMIT = 100    # عدد الطلبات المسموحة
    _WINDOW = 3600  # نافذة زمنية ثانية (ساعة واحدة)

    def process_request(self, request):
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            ip_address = self._get_client_ip(request)
            cache_key = f'rate_limit:{ip_address}'

            request_count = cache.get(cache_key, 0)
            if request_count >= self._LIMIT:
                logger.warning('Rate limit exceeded for IP: %s', ip_address)
                return HttpResponseForbidden('تم تجاوز حد الطلبات المسموح به. حاول لاحقًا.')

            # زيادة العداد — cache.incr يفشل إذا لم يكن المفتاح موجودًا
            try:
                cache.incr(cache_key)
            except ValueError:
                cache.set(cache_key, 1, self._WINDOW)

        return None

    @staticmethod
    def _get_client_ip(request):
        """استخراج IP العميل الحقيقي مع معالجة X-Forwarded-For بأمان."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if x_forwarded_for:
            # الأول في القائمة هو IP العميل — نُنظّف المسافات لمنع التزوير
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')


class LoggingMiddleware(MiddlewareMixin):
    """وسيط تسجيل الطلبات والاستجابات المهمة."""

    def process_request(self, request):
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            logger.info(
                '%s %s — IP: %s',
                request.method,
                request.path,
                self._get_client_ip(request),
            )
        return None

    def process_response(self, request, response):
        if response.status_code >= 400:
            logger.warning(
                '%s %s — Status: %s',
                request.method,
                request.path,
                response.status_code,
            )
        return response

    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')


class MaintenanceMiddleware(MiddlewareMixin):
    """وسيط وضع الصيانة — يحجب الوصول للزوار ويُتيحه للمديرين."""

    def process_request(self, request):
        if not getattr(settings, 'MAINTENANCE_MODE', False):
            return None

        # المديرون يمرون دائمًا
        if request.user.is_authenticated and request.user.is_staff:
            return None

        return HttpResponseForbidden('الموقع في وضع الصيانة. يرجى المحاولة لاحقًا.')
