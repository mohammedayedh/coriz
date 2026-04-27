"""
Django management command لإضافة مصادر OSINT الجديدة (بدون API)
"""

from django.core.management.base import BaseCommand
from osint_tools.models import OSINTTool


class Command(BaseCommand):
    help = 'إضافة مصادر OSINT الجديدة التي تعمل بدون API'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 بدء إضافة مصادر OSINT الجديدة...'))
        
        tools_data = [
            {
                'name': 'Certificate Transparency',
                'slug': 'cert-transparency',
                'description': 'البحث عن النطاقات الفرعية من خلال شهادات SSL/TLS المسجلة في سجلات Certificate Transparency. يكتشف جميع النطاقات الفرعية حتى المخفية.',
                'tool_type': 'domain',
                'source_type': 'open',
                'required_clearance': 'L1',
                'status': 'active',
                'icon': 'fas fa-certificate',
                'color': '#10b981',
                'requires_auth': False,
                'api_key_required': False,
                'rate_limit': 100,
                'timeout': 30,
                'tool_path': 'osint_tools/scrapers',
                'executable_name': 'cert_transparency.py',
                'command_template': 'python {tool_path}/{executable_name} --domain {target}',
                'config_schema': {
                    'search_type': 'domain',
                    'example': 'example.com',
                    'description_extra': 'يبحث في سجلات Certificate Transparency لاكتشاف جميع النطاقات الفرعية المسجلة في شهادات SSL/TLS',
                    'features': [
                        'اكتشاف النطاقات الفرعية المخفية',
                        'معلومات الشهادات وتواريخ الإصدار',
                        'تاريخ النطاقات الفرعية',
                        'بدون حاجة لـ API key'
                    ],
                    'output_fields': [
                        'subdomains',
                        'certificates',
                        'issuer',
                        'validity_dates'
                    ]
                },
                'supported_formats': ['json', 'txt', 'csv']
            },
            {
                'name': 'Wayback Machine',
                'slug': 'wayback-machine',
                'description': 'البحث في أرشيف الإنترنت للحصول على نسخ قديمة من المواقع. يكشف المحتوى المحذوف والتغييرات التاريخية.',
                'tool_type': 'domain',
                'source_type': 'open',
                'required_clearance': 'L1',
                'status': 'active',
                'icon': 'fas fa-history',
                'color': '#3b82f6',
                'requires_auth': False,
                'api_key_required': False,
                'rate_limit': 100,
                'timeout': 30,
                'tool_path': 'osint_tools/scrapers',
                'executable_name': 'wayback_machine.py',
                'command_template': 'python {tool_path}/{executable_name} --url {target}',
                'config_schema': {
                    'search_type': 'domain or url',
                    'example': 'example.com',
                    'description_extra': 'يبحث في أرشيف Archive.org للحصول على نسخ قديمة من المواقع والصفحات المحذوفة',
                    'features': [
                        'النسخ المحفوظة من المواقع',
                        'تاريخ التغييرات',
                        'المحتوى المحذوف',
                        'إحصائيات تاريخية'
                    ],
                    'output_fields': [
                        'snapshots',
                        'first_snapshot',
                        'last_snapshot',
                        'years_active',
                        'archive_urls'
                    ]
                },
                'supported_formats': ['json', 'txt', 'html']
            },
            {
                'name': 'Google Dorks',
                'slug': 'google-dorks',
                'description': 'البحث المتقدم في Google لاكتشاف ملفات مكشوفة، معلومات حساسة، وثغرات أمنية باستخدام استعلامات متقدمة.',
                'tool_type': 'general',
                'source_type': 'open',
                'required_clearance': 'L1',
                'status': 'active',
                'icon': 'fab fa-google',
                'color': '#f59e0b',
                'requires_auth': False,
                'api_key_required': False,
                'rate_limit': 50,
                'timeout': 30,
                'tool_path': 'osint_tools/scrapers',
                'executable_name': 'google_dorks.py',
                'command_template': 'python {tool_path}/{executable_name} --target {target}',
                'config_schema': {
                    'search_type': 'domain, email, username, or custom dork',
                    'example': 'example.com',
                    'description_extra': 'يستخدم استعلامات Google المتقدمة (Dorks) لاكتشاف معلومات حساسة وملفات مكشوفة',
                    'features': [
                        'اكتشاف ملفات PDF, DOC, XLS المكشوفة',
                        'البحث عن معلومات حساسة',
                        'اكتشاف صفحات الإدارة',
                        'فحص الثغرات الأمنية'
                    ],
                    'output_fields': [
                        'exposed_files',
                        'sensitive_info',
                        'admin_pages',
                        'vulnerabilities'
                    ],
                    'dork_categories': [
                        'files',
                        'sensitive',
                        'directories',
                        'vulnerabilities'
                    ]
                },
                'supported_formats': ['json', 'txt', 'html']
            },
            {
                'name': 'Reverse Image Search',
                'slug': 'reverse-image',
                'description': 'البحث العكسي عن الصور في محركات متعددة (Google, Yandex, TinEye, Bing) لإيجاد مصادر الصورة والصور المشابهة.',
                'tool_type': 'general',
                'source_type': 'open',
                'required_clearance': 'L1',
                'status': 'active',
                'icon': 'fas fa-image',
                'color': '#8b5cf6',
                'requires_auth': False,
                'api_key_required': False,
                'rate_limit': 100,
                'timeout': 30,
                'tool_path': 'osint_tools/scrapers',
                'executable_name': 'reverse_image.py',
                'command_template': 'python {tool_path}/{executable_name} --image {target}',
                'config_schema': {
                    'search_type': 'رابط صورة',
                    'example': 'https://example.com/image.jpg',
                    'description_extra': 'يبحث عن الصورة في 4 محركات بحث رئيسية لإيجاد المصدر الأصلي والصور المشابهة',
                    'usage_guide': 'أدخل رابط الصورة (URL) للبحث عنها في محركات متعددة',
                    'input_format': 'رابط مباشر للصورة (يجب أن ينتهي بـ .jpg, .png, .gif, etc.)',
                    'features': [
                        'البحث في 4 محركات رئيسية (Google, Yandex, TinEye, Bing)',
                        'إيجاد المصدر الأصلي للصورة',
                        'اكتشاف الصور المشابهة والمعدلة',
                        'حساب Hash للصورة (MD5, SHA256)',
                        'معلومات حجم الصورة',
                        'روابط مباشرة لنتائج كل محرك',
                        'كشف الصور المسروقة أو المعاد استخدامها',
                        'التحقق من أصالة الصور',
                        'سريع (أقل من 5 ثواني)'
                    ],
                    'output_fields': [
                        'search_urls',
                        'similar_images',
                        'image_hash',
                        'image_metadata',
                        'image_size',
                        'md5',
                        'sha256'
                    ],
                    'supported_engines': [
                        'Google Images - الأكثر شمولاً',
                        'Yandex Images - ممتاز للصور الروسية',
                        'TinEye - متخصص في البحث العكسي',
                        'Bing Images - تغطية واسعة'
                    ],
                    'use_cases': [
                        'التحقق من أصالة الصور',
                        'إيجاد مصدر الصورة الأصلي',
                        'كشف الصور المسروقة',
                        'البحث عن صور عالية الجودة',
                        'التحقق من هوية الأشخاص',
                        'كشف الحسابات المزيفة'
                    ],
                    'tips': [
                        'استخدم صور واضحة وعالية الجودة للحصول على نتائج أفضل',
                        'Google وYandex يعطيان أفضل النتائج للصور الشائعة',
                        'TinEye ممتاز لتتبع استخدام الصور عبر الإنترنت',
                        'Hash الصورة مفيد للمقارنة والتحقق من التطابق'
                    ]
                },
                'supported_formats': ['json', 'txt', 'html']
            },
            {
                'name': 'IP Geolocation',
                'slug': 'ip-geolocation',
                'description': 'تحديد الموقع الجغرافي لعناوين IP مع معلومات ISP والشبكة. يستخدم خدمات مجانية متعددة بدون API key.',
                'tool_type': 'ip',
                'source_type': 'open',
                'required_clearance': 'L1',
                'status': 'active',
                'icon': 'fas fa-map-marker-alt',
                'color': '#ef4444',
                'requires_auth': False,
                'api_key_required': False,
                'rate_limit': 150,
                'timeout': 30,
                'tool_path': 'osint_tools/scrapers',
                'executable_name': 'ip_geolocation.py',
                'command_template': 'python {tool_path}/{executable_name} --ip {target}',
                'config_schema': {
                    'search_type': 'عنوان IP',
                    'example': '8.8.8.8',
                    'description_extra': 'يحدد الموقع الجغرافي لعنوان IP مع معلومات ISP، المنظمة، والشبكة بدقة عالية',
                    'usage_guide': 'أدخل عنوان IP (IPv4) للحصول على معلومات جغرافية شاملة',
                    'input_format': 'عنوان IP صالح (مثال: 8.8.8.8 أو 1.1.1.1)',
                    'features': [
                        'الموقع الجغرافي الدقيق (البلد، المدينة، الإحداثيات)',
                        'معلومات ISP ومزود الخدمة',
                        'رقم AS (Autonomous System) والشبكة',
                        'كشف البروكسي والخوادم',
                        'كشف خدمات الاستضافة',
                        'المنطقة الزمنية',
                        'رابط مباشر لخريطة Google Maps',
                        'دعم البحث عن عدة IPs دفعة واحدة',
                        'تحليل نطاقات IP',
                        'سريع جداً (أقل من 2 ثانية)'
                    ],
                    'output_fields': [
                        'country',
                        'city',
                        'coordinates',
                        'isp',
                        'organization',
                        'as_number',
                        'timezone',
                        'is_proxy',
                        'is_hosting',
                        'map_url'
                    ],
                    'use_cases': [
                        'تتبع مصدر الهجمات الإلكترونية',
                        'التحقق من موقع الخوادم',
                        'كشف استخدام VPN أو Proxy',
                        'تحليل حركة المرور',
                        'التحقق من مواقع المستخدمين'
                    ],
                    'tips': [
                        'يمكن البحث عن أي IP عام (ليس خاص)',
                        'النتائج دقيقة بنسبة 90-95%',
                        'بعض IPs قد تظهر موقع مزود الخدمة وليس الموقع الفعلي',
                        'استخدم رابط الخريطة لرؤية الموقع بصرياً'
                    ]
                },
                'supported_formats': ['json', 'txt', 'html']
            },
            {
                'name': 'Email OSINT',
                'slug': 'email-osint',
                'description': 'تحليل شامل للبريد الإلكتروني: التحقق من الصيغة، تحليل النطاق، Gravatar، ملفات اجتماعية محتملة، وتوليد تنويعات البريد.',
                'tool_type': 'email',
                'source_type': 'open',
                'required_clearance': 'L1',
                'status': 'active',
                'icon': 'fas fa-envelope',
                'color': '#06b6d4',
                'requires_auth': False,
                'api_key_required': False,
                'rate_limit': 200,
                'timeout': 30,
                'tool_path': 'osint_tools/scrapers',
                'executable_name': 'email_osint.py',
                'command_template': 'python {tool_path}/{executable_name} --email {target}',
                'config_schema': {
                    'search_type': 'عنوان بريد إلكتروني',
                    'example': 'user@example.com',
                    'description_extra': 'يحلل البريد الإلكتروني بشكل شامل: النطاق، Gravatar، ملفات اجتماعية محتملة، وتنويعات البريد',
                    'usage_guide': 'أدخل عنوان البريد الإلكتروني للحصول على تحليل شامل',
                    'input_format': 'عنوان بريد إلكتروني صالح (مثال: user@domain.com)',
                    'features': [
                        'التحقق من صحة صيغة البريد الإلكتروني',
                        'تحليل النطاق (مجاني/مؤقت/تجاري)',
                        'التعرف على مزود البريد (Gmail, Yahoo, Outlook, etc.)',
                        'كشف البريد المؤقت (Disposable Email)',
                        'التحقق من وجود حساب Gravatar',
                        'الحصول على صورة Gravatar إن وجدت',
                        'اقتراح ملفات اجتماعية محتملة (GitHub, Twitter, LinkedIn, etc.)',
                        'توليد تنويعات محتملة للبريد الإلكتروني',
                        'استخراج عناوين البريد من النصوص',
                        'توصيات أمنية',
                        'سريع جداً (أقل من ثانية واحدة)'
                    ],
                    'output_fields': [
                        'format_valid',
                        'domain_info',
                        'provider_name',
                        'is_free_provider',
                        'is_disposable',
                        'gravatar',
                        'social_profiles',
                        'email_variations',
                        'security_recommendations'
                    ],
                    'domain_analysis': [
                        'نوع المزود (مجاني/تجاري)',
                        'اسم المزود إن كان معروفاً',
                        'كشف البريد المؤقت',
                        'سجلات MX (إن أمكن)'
                    ],
                    'social_platforms': [
                        'GitHub',
                        'Twitter',
                        'LinkedIn',
                        'Instagram',
                        'Facebook',
                        'وغيرها...'
                    ],
                    'use_cases': [
                        'التحقق من صحة البريد الإلكتروني',
                        'البحث عن ملفات اجتماعية',
                        'كشف البريد المؤقت أو المزيف',
                        'توليد قائمة بريد محتملة',
                        'التحقق من هوية الأشخاص',
                        'البحث عن معلومات إضافية'
                    ],
                    'tips': [
                        'Gravatar يستخدم من قبل ملايين المواقع',
                        'البريد المؤقت غالباً يستخدم للتسجيل المؤقت',
                        'تنويعات البريد مفيدة للبحث عن حسابات متعددة',
                        'الملفات الاجتماعية المقترحة تحتاج تحقق يدوي'
                    ],
                    'privacy_note': 'جميع المعلومات المستخرجة من مصادر عامة ومتاحة للجميع'
                },
                'supported_formats': ['json', 'txt', 'html']
            }
        ]
        
        added_count = 0
        updated_count = 0
        
        for tool_data in tools_data:
            tool, created = OSINTTool.objects.update_or_create(
                slug=tool_data['slug'],
                defaults=tool_data
            )
            
            if created:
                added_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ تمت إضافة: {tool.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'🔄 تم تحديث: {tool.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✨ اكتمل! تمت إضافة {added_count} أداة جديدة وتحديث {updated_count} أداة موجودة.'
            )
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n📊 الأدوات المضافة:'
            )
        )
        
        for tool_data in tools_data:
            self.stdout.write(f"   • {tool_data['name']} ({tool_data['slug']})")
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n💡 لاختبار الأدوات، قم بتشغيل:'
            )
        )
        self.stdout.write('   python osint_tools/scrapers/cert_transparency.py')
        self.stdout.write('   python osint_tools/scrapers/wayback_machine.py')
        self.stdout.write('   python osint_tools/scrapers/google_dorks.py')
        self.stdout.write('   python osint_tools/scrapers/reverse_image.py')
        self.stdout.write('   python osint_tools/scrapers/ip_geolocation.py')
        self.stdout.write('   python osint_tools/scrapers/email_osint.py')
