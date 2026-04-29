import subprocess
import json
import os
import logging
import time
import shlex
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from .models import OSINTSession, OSINTResult, OSINTReport, OSINTActivityLog

logger = logging.getLogger(__name__)


class OSINTToolRunner:
    """فئة لتشغيل أدوات OSINT"""
    
    # خريطة slug → scraper مباشر
    SCRAPER_MAP = {
        'sherlock':            ('osint_tools.scrapers.social_investigator', 'SocialInvestigatorScraper', 'investigate'),
        'social-investigator': ('osint_tools.scrapers.social_investigator', 'SocialInvestigatorScraper', 'investigate'),
        'github-osint':        ('osint_tools.scrapers.github_osint',        'GitHubOSINT',               'get_user_info'),
        'email-osint':         ('osint_tools.scrapers.email_osint',         'EmailOSINT',                'analyze_email'),
        'breach-detector':     ('osint_tools.scrapers.breach_detector',     'BreachDetectorScraper',     'search_email'),
        'ip-geolocation':      ('osint_tools.scrapers.ip_geolocation',      'IPGeolocationScraper',      'lookup'),
        'cert-transparency':   ('osint_tools.scrapers.cert_transparency',   'CertTransparencyScraper',   'search'),
        'wayback-machine':     ('osint_tools.scrapers.wayback_machine',     'WaybackMachineScraper',     'search_snapshots'),
        'google-dorks':        ('osint_tools.scrapers.google_dorks',        'GoogleDorksScraper',        'search'),
        'subdomain-enum':      ('osint_tools.scrapers.cert_transparency',   'CertTransparencyScraper',   'search'),
    }

    def __init__(self, session):
        self.session = session
        self.tool = session.tool
        self.target = session.target
        self.config = session.config
        self.options = session.options

    def _run_scraper_directly(self):
        """تشغيل الـ scraper مباشرة كـ Python class"""
        slug = self.tool.slug
        if slug not in self.SCRAPER_MAP:
            return None  # لا يوجد scraper مباشر، جرب shell

        module_path, class_name, method_name = self.SCRAPER_MAP[slug]
        import importlib
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        instance = cls()
        method = getattr(instance, method_name)
        result = method(self.target)
        return result

    def run(self):
        """تشغيل الأداة"""
        try:
            logger.info(f"بدء تشغيل الأداة {self.tool.name} للهدف {self.target}")
            
            self.session.status = 'running'
            self.session.progress = 10
            self.session.current_step = 'جاري التهيئة...'
            self.session.started_at = timezone.now()
            self.session.save()

            # --- محاولة 1: scraper مباشر ---
            scraper_result = None
            try:
                scraper_result = self._run_scraper_directly()
            except Exception as scraper_err:
                logger.warning(f"فشل الـ scraper المباشر لـ {self.tool.slug}: {scraper_err}")

            if scraper_result is not None:
                self.session.progress = 70
                self.session.current_step = 'جاري معالجة النتائج...'
                self.session.save()
                self._process_scraper_results(scraper_result)
            else:
                # --- محاولة 2: أمر shell ---
                command = self._build_command()
                logger.info(f"الأمر: {' '.join(command)}")
                self.session.progress = 30
                self.session.current_step = 'جاري تشغيل الأداة...'
                self.session.save()
                result = self._execute_command(command)
                self.session.progress = 70
                self.session.current_step = 'جاري معالجة النتائج...'
                self.session.save()
                self._process_results(result)

            self.session.status = 'completed'
            self.session.progress = 100
            self.session.current_step = 'تم الانتهاء بنجاح!'
            self.session.completed_at = timezone.now()
            self.session.save()
            logger.info(f"تم تشغيل الأداة {self.tool.name} بنجاح")

        except Exception as e:
            logger.error(f"خطأ في تشغيل الأداة {self.tool.name}: {e}")
            self.session.status = 'failed'
            self.session.progress = 0
            self.session.current_step = f'فشل في التشغيل: {str(e)}'
            self.session.error_message = str(e)
            self.session.completed_at = timezone.now()
            self.session.save()

    def _process_scraper_results(self, data):
        """معالجة نتائج الـ scraper المباشر وحفظها في DB"""
        results_list = []

        if isinstance(data, dict):
            results_list = data.get('results', [])
            # إذا لم يكن هناك results لكن يوجد بيانات مفيدة
            if not results_list and data.get('success'):
                results_list = [{'title': f"نتيجة {self.tool.name}", 'description': str(data), 'type': 'general', 'confidence': 'medium'}]
        elif isinstance(data, list):
            results_list = data

        if not results_list:
            r_type = self.tool.tool_type or 'other'
            if r_type == 'general':
                r_type = 'other'
                
            # لا نتائج - أنشئ نتيجة تفيد بذلك
            OSINTResult.objects.create(
                session=self.session,
                result_type=r_type,
                title=f"فحص {self.tool.name}: {self.target}",
                description="تم الفحص ولم يتم العثور على نتائج",
                raw_data=data if isinstance(data, dict) else {'data': str(data)},
                confidence='low',
                confidence_score=0.3,
                source=self.tool.name,
                tags=[self.tool.tool_type or 'general', 'no_results'],
                metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
            )
        else:
            for item in results_list:
                if not isinstance(item, dict):
                    continue
                    
                r_type = item.get('type')
                if not r_type:
                    r_type = self.tool.tool_type or 'other'
                if r_type == 'general':
                    r_type = 'other'
                    
                raw_title = item.get('title', f"نتيجة {self.tool.name}")
                if len(raw_title) > 200:
                    raw_title = raw_title[:196] + '...'
                    
                OSINTResult.objects.create(
                    session=self.session,
                    result_type=r_type,
                    title=raw_title,
                    description=item.get('description', ''),
                    url=item.get('url', ''),
                    raw_data=item,
                    confidence=item.get('confidence', 'medium'),
                    confidence_score=0.9 if item.get('confidence') == 'high' else 0.5,
                    source=self.tool.name,
                    tags=[self.tool.tool_type or 'general'],
                    metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                )

        from .models import OSINTResult as R
        self.session.results_count = R.objects.filter(session=self.session).count()
        self.session.save(update_fields=['results_count'])
    
    def test(self):
        """اختبار الأداة"""
        try:
            # اختبار بسيط - التحقق من وجود الملف التنفيذي
            tool_path = os.path.join(settings.BASE_DIR, 'open_tool', self.tool.tool_path)
            executable_path = os.path.join(tool_path, self.tool.executable_name)
            
            if not os.path.exists(executable_path):
                return {
                    'success': False,
                    'message': f'الملف التنفيذي غير موجود: {executable_path}',
                    'error': 'File not found'
                }
            
            # اختبار بسيط للأدوات
            if self.tool.name == 'Sherlock':
                test_command = ['python', self.tool.executable_name, '--help']
            elif self.tool.name == 'Infoga':
                test_command = ['python', self.tool.executable_name, '--help']
            elif self.tool.name == 'GHunt':
                test_command = ['python', self.tool.executable_name, '--help']
            elif self.tool.name == 'SpiderFoot':
                test_command = ['python', self.tool.executable_name, '-h']
            else:
                # للأدوات الأخرى، نكتفي بالتحقق من وجود الملف
                return {
                    'success': True,
                    'message': 'الملف التنفيذي موجود',
                    'error': None
                }
            
            result = subprocess.run(
                test_command, 
                cwd=tool_path,
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            return {
                'success': result.returncode == 0 or 'help' in result.stdout.lower() or 'usage' in result.stdout.lower(),
                'message': 'تم الاختبار بنجاح' if result.returncode == 0 else 'الأداة موجودة ولكن قد تحتاج إعدادات إضافية',
                'error': result.stderr if result.returncode != 0 else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'انتهت مهلة الاختبار',
                'error': 'Timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'message': 'حدث خطأ في الاختبار',
                'error': str(e)
            }
    
    def _build_command(self):
        """بناء أمر تشغيل الأداة"""
        # استبدال المتغيرات في قالب الأمر
        command_template = self.tool.command_template
        
        # تجهيز المتغيرات الديناميكية للمسارات
        # نستخدم os.path.join لضمان التوافق مع أنظمة التشغيل
        tool_path = self.tool.tool_path or ''
        executable_name = self.tool.executable_name or ''
        full_executable_path = os.path.join(tool_path, executable_name)
        
        # دمج المتغيرات الأساسية مع متغيرات الإعدادات
        format_kwargs = {
            'target': self.target,
            'tool_path': tool_path,
            'executable_name': executable_name,
            'executable': full_executable_path,
            **self.config
        }
        
        try:
            command_str = command_template.format(**format_kwargs)
            
            # ضمان استخدام مسار البايثون الصحيح (سواء البيئة الافتراضية أو النظام)
            import sys
            import os
            
            python_exe = sys.executable
            # إذا كنا داخل بيئة افتراضية، تأكد من استخدام البايثون الخاص بها
            venv_base = os.environ.get('VIRTUAL_ENV')
            if venv_base:
                venv_python = os.path.join(venv_base, 'bin', 'python')
                if os.path.exists(venv_python):
                    python_exe = venv_python
            # كحل احتياطي للسيرفر
            elif os.path.exists('/srv/coriza/venv/bin/python'):
                python_exe = '/srv/coriza/venv/bin/python'
                
            if command_str.startswith('python3 '):
                command_str = command_str.replace('python3 ', f'{python_exe} ', 1)
            elif command_str.startswith('python '):
                command_str = command_str.replace('python ', f'{python_exe} ', 1)
                
            # استخدام shlex لتقسيم الأمر بشكل احترافي مع مراعاة النصوص المقتبسة
            return shlex.split(command_str)
        except KeyError as e:
            logger.error(f"متغير مفقود في قالب الأداة {self.tool.slug}: {e}")
            raise Exception(f"خطأ في قالب الأداة: المتغير {e} غير معرف")
    
    def _execute_command(self, command):
        """تنفيذ الأمر"""
        try:
            # تشغيل الأمر من المجلد الحالي (للأدوات المثبتة عالمياً)
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.tool.timeout,
                encoding='utf-8',
                errors='ignore'
            )
            
            return {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except subprocess.TimeoutExpired:
            raise Exception("انتهت المهلة الزمنية لتشغيل الأداة")
        except Exception as e:
            raise Exception(f"خطأ في تنفيذ الأمر: {e}")
    
    def _process_results(self, result):
        """معالجة نتائج الأداة"""
        if result['returncode'] != 0:
            # حتى لو فشل الأمر، نحاول معالجة النتائج المتاحة
            if result['stdout']:
                logger.warning(f"الأمر فشل لكن يوجد مخرجات: {result['stdout'][:200]}")
            else:
                raise Exception(f"فشل في تشغيل الأداة: {result['stderr']}")
        
        # معالجة النتائج حسب نوع الأداة
        if self.tool.tool_type == 'email':
            self._process_email_results(result['stdout'])
        elif self.tool.tool_type == 'username':
            self._process_username_results(result['stdout'])
        elif self.tool.tool_type == 'domain':
            self._process_domain_results(result['stdout'])
        elif self.tool.tool_type == 'ip':
            self._process_ip_results(result['stdout'])
        else:
            self._process_general_results(result['stdout'])
        
        # تحديث عدد النتائج
        from .models import OSINTResult
        self.session.results_count = OSINTResult.objects.filter(session=self.session).count()
        self.session.save(update_fields=['results_count'])
    
    def _generate_summary(self, data):
        """توليد وصف تلقائي من بيانات الـ JSON"""
        if not isinstance(data, dict):
            return "تم جمع المعلومات بنجاح."
            
        summary_parts = []
        # التحقق من وجود مفاتيح معينة شائعة
        if 'total_found' in data:
            summary_parts.append(f"تم العثور على {data['total_found']} نتيجة")
        if 'breaches' in data and isinstance(data['breaches'], list):
            summary_parts.append(f"يوجد {len(data['breaches'])} تسريب")
        if 'status' in data:
            if isinstance(data['status'], str):
                summary_parts.append(f"الحالة: {data['status']}")
            elif isinstance(data['status'], dict) and 'status' in data['status']:
                summary_parts.append(f"الحالة: {data['status']['status']}")
                
        # إذا لم نجد مفاتيح شائعة، نستخرج أول 3 مفاتيح
        if not summary_parts:
            keys = [k for k in data.keys() if k not in ['target', 'domain', 'email', 'ip', 'status', 'error', 'success', 'data']][:3]
            if keys:
                summary_parts.append(f"تم تحليل: {', '.join(keys)}")
                
        # التعامل مع حالة القوائم داخل البيانات
        list_keys = [k for k, v in data.items() if isinstance(v, list)]
        if list_keys and not 'breaches' in data:
            summary_parts.append(f"يحتوي على قوائم بيانات: {', '.join(list_keys[:2])}")
            
        return " | ".join(summary_parts) if summary_parts else "تمت عملية الفحص وجمع البيانات الخام بنجاح."

    def _process_email_results(self, output):
        """معالجة نتائج البريد الإلكتروني"""
        try:
            # محاولة تحليل JSON
            if output and output.strip():
                data = json.loads(output)
                
                if isinstance(data, dict):
                    # إنشاء نتيجة واحدة
                    desc = data.get('message') or data.get('description') or self._generate_summary(data)
                    OSINTResult.objects.create(
                        session=self.session,
                        result_type='email',
                        title=f"معلومات البريد الإلكتروني: {self.target}",
                        description=desc,
                        url=data.get('url', ''),
                        raw_data=data,
                        confidence='high' if data.get('success', False) else 'medium',
                        confidence_score=0.9 if data.get('success', False) else 0.6,
                        source=self.tool.name,
                        tags=['email', 'verification'],
                        metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                    )
                    
                    # معالجة النتائج الفرعية
                    if 'results' in data and isinstance(data['results'], list):
                        for item in data['results']:
                            OSINTResult.objects.create(
                                session=self.session,
                                result_type='email',
                                title=item.get('source', f"نتيجة للبريد: {self.target}"),
                                description=item.get('description', ''),
                                url=item.get('url', ''),
                                raw_data=item,
                                confidence=item.get('confidence', 'medium'),
                                confidence_score=0.8 if item.get('confidence') == 'high' else 0.5,
                                source=self.tool.name,
                                tags=['email', item.get('type', 'general')],
                                metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                            )
                elif isinstance(data, list):
                    # إنشاء عدة نتائج
                    for item in data:
                        OSINTResult.objects.create(
                            session=self.session,
                            result_type='email',
                            title=item.get('title', f"نتيجة للبريد: {self.target}"),
                            description=item.get('description', ''),
                            url=item.get('url', ''),
                            raw_data=item,
                            confidence=item.get('confidence', 'medium'),
                            confidence_score=item.get('confidence_score', 0.5),
                            source=self.tool.name,
                            tags=item.get('tags', ['email']),
                            metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                        )
            else:
                # إذا لم يكن هناك مخرجات، إنشاء نتيجة افتراضية
                OSINTResult.objects.create(
                    session=self.session,
                    result_type='email',
                    title=f"فحص البريد الإلكتروني: {self.target}",
                    description="تم فحص البريد الإلكتروني ولكن لم يتم العثور على نتائج",
                    raw_data={'raw_output': output or 'No output'},
                    confidence='low',
                    confidence_score=0.3,
                    source=self.tool.name,
                    tags=['email', 'no_results'],
                    metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                )
                    
        except json.JSONDecodeError:
            # معالجة النص العادي
            if output and output.strip():
                OSINTResult.objects.create(
                    session=self.session,
                    result_type='email',
                    title=f"نتيجة للبريد: {self.target}",
                    description=output.strip(),
                    raw_data={'raw_output': output.strip()},
                    confidence='low',
                    confidence_score=0.3,
                    source=self.tool.name,
                    tags=['email', 'raw'],
                    metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                )
            else:
                # إنشاء نتيجة افتراضية
                OSINTResult.objects.create(
                    session=self.session,
                    result_type='email',
                    title=f"فحص البريد الإلكتروني: {self.target}",
                    description="تم فحص البريد الإلكتروني",
                    raw_data={'raw_output': 'No output'},
                    confidence='low',
                    confidence_score=0.3,
                    source=self.tool.name,
                    tags=['email', 'default'],
                    metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                )
    
    def _process_username_results(self, output):
        """معالجة نتائج اسم المستخدم"""
        try:
            if output and output.strip():
                data = json.loads(output)
                
                if isinstance(data, dict):
                    # إنشاء نتيجة واحدة
                    OSINTResult.objects.create(
                        session=self.session,
                        result_type='username',
                        title=f"معلومات اسم المستخدم: {self.target}",
                        description=data.get('message', 'تم البحث عن اسم المستخدم'),
                        url=data.get('url', ''),
                        raw_data=data,
                        confidence='high' if data.get('success', False) else 'medium',
                        confidence_score=0.9 if data.get('success', False) else 0.6,
                        source=self.tool.name,
                        tags=['username', 'search'],
                        metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                    )
                    
                    # معالجة النتائج الفرعية
                    if 'results' in data and isinstance(data['results'], list):
                        for item in data['results']:
                            OSINTResult.objects.create(
                                session=self.session,
                                result_type='social_media',
                                title=item.get('platform', f"نتيجة لاسم المستخدم: {self.target}"),
                                description=item.get('description', ''),
                                url=item.get('url', ''),
                                raw_data=item,
                                confidence=item.get('confidence', 'medium'),
                                confidence_score=0.8 if item.get('confidence') == 'high' else 0.5,
                                source=self.tool.name,
                                tags=['username', item.get('status', 'unknown')],
                                metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                            )
                elif isinstance(data, list):
                    # إنشاء عدة نتائج
                    for item in data:
                        OSINTResult.objects.create(
                            session=self.session,
                            result_type='social_media',
                            title=f"حساب {item.get('platform', 'غير معروف')}: {self.target}",
                            description=item.get('description', ''),
                            url=item.get('url', ''),
                            raw_data=item,
                            confidence='high' if item.get('found', False) else 'low',
                            confidence_score=0.9 if item.get('found', False) else 0.2,
                            source=self.tool.name,
                            tags=['username', 'social_media', item.get('platform', 'unknown')],
                            metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                        )
            else:
                # إنشاء نتيجة افتراضية
                OSINTResult.objects.create(
                    session=self.session,
                    result_type='username',
                    title=f"فحص اسم المستخدم: {self.target}",
                    description="تم فحص اسم المستخدم ولكن لم يتم العثور على نتائج",
                    raw_data={'raw_output': output or 'No output'},
                    confidence='low',
                    confidence_score=0.3,
                    source=self.tool.name,
                    tags=['username', 'no_results'],
                    metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                )
                    
        except json.JSONDecodeError:
            # معالجة النص العادي من Sherlock
            if not output or not output.strip():
                logger.info("لا توجد مخرجات من Sherlock")
                OSINTResult.objects.create(
                    session=self.session,
                    result_type='username',
                    title=f"فحص اسم المستخدم: {self.target}",
                    description="تم فحص اسم المستخدم ولكن لم يتم العثور على نتائج",
                    raw_data={'message': 'No output'},
                    confidence='low',
                    confidence_score=0.3,
                    source=self.tool.name,
                    tags=['username', 'no_results'],
                    metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                )
                return
                
            output_clean = output.strip()
            lines = output_clean.split('\n')
            found_profiles = []
            
            for line in lines:
                line = line.strip()
                # البحث عن السطور التي تحتوي على [+] (حسابات موجودة)
                if line.startswith('[+]'):
                    # تحليل السطر: [+] Platform: URL
                    parts = line[3:].split(':', 1)
                    if len(parts) == 2:
                        platform = parts[0].strip()
                        url = parts[1].strip()
                        found_profiles.append({'platform': platform, 'url': url})
            
            # إنشاء نتيجة لكل حساب موجود
            for profile in found_profiles:
                OSINTResult.objects.create(
                    session=self.session,
                    result_type='social_media',
                    title=f"{profile['platform']}: {self.target}",
                    description=f"تم العثور على حساب في {profile['platform']}",
                    url=profile['url'],
                    raw_data={'platform': profile['platform'], 'url': profile['url'], 'username': self.target},
                    confidence='high',
                    confidence_score=0.8,
                    source=self.tool.name,
                    tags=['username', 'social_media', profile['platform'].lower().replace(' ', '_')],
                    metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                )
            
            # إذا لم نجد أي حسابات
            if not found_profiles:
                logger.info(f"لم يتم العثور على حسابات لـ {self.target}")
                OSINTResult.objects.create(
                    session=self.session,
                    result_type='username',
                    title=f"فحص اسم المستخدم: {self.target}",
                    description="تم فحص اسم المستخدم في مئات المواقع ولكن لم يتم العثور على حسابات",
                    raw_data={'raw_output': output_clean[:1000]},
                    confidence='low',
                    confidence_score=0.3,
                    source=self.tool.name,
                    tags=['username', 'no_results'],
                    metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                )
            else:
                logger.info(f"تم العثور على {len(found_profiles)} حساب لـ {self.target}")
    
    def _process_domain_results(self, output):
        """معالجة نتائج النطاق"""
        try:
            data = json.loads(output)
            
            if isinstance(data, dict):
                desc = data.get('description') or data.get('message') or self._generate_summary(data)
                OSINTResult.objects.create(
                    session=self.session,
                    result_type='domain',
                    title=f"معلومات النطاق: {self.target}",
                    description=desc,
                    url=data.get('url', ''),
                    raw_data=data,
                    confidence='high',
                    confidence_score=0.8,
                    source=self.tool.name,
                    tags=['domain', 'whois', 'dns'],
                    metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                )
                
        except json.JSONDecodeError:
            # معالجة النص العادي من theHarvester
            if not output or not output.strip():
                logger.info("لا توجد مخرجات للمعالجة")
                # إنشاء نتيجة تفيد بعدم وجود معلومات
                OSINTResult.objects.create(
                    session=self.session,
                    result_type='domain',
                    title=f"فحص النطاق: {self.target}",
                    description="تم فحص النطاق ولكن لم يتم العثور على معلومات متاحة",
                    raw_data={'message': 'No data found', 'target': self.target},
                    confidence='low',
                    confidence_score=0.3,
                    source=self.tool.name,
                    tags=['domain', 'no_results'],
                    metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                )
                return
                
            output_clean = output.strip()
            
            # تجاهل رسائل الإعدادات
            ignore_patterns = ['Created default', 'proxies.yaml', 'config.yaml']
            if any(pattern in output_clean for pattern in ignore_patterns):
                logger.info(f"تجاهل رسالة إعدادات: {output_clean[:100]}")
                # لكن لا نتوقف - نستمر في البحث عن نتائج
            
            # تحليل مخرجات theHarvester
            emails = []
            hosts = []
            ips = []
            
            lines = output_clean.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('*') or line.startswith('['):
                    continue
                    
                # تحديد القسم الحالي
                if 'email' in line.lower() or 'بريد' in line.lower():
                    current_section = 'emails'
                    continue
                elif 'host' in line.lower() or 'مضيف' in line.lower():
                    current_section = 'hosts'
                    continue
                elif 'ip' in line.lower() and 'address' in line.lower():
                    current_section = 'ips'
                    continue
                elif 'No emails found' in line or 'No hosts found' in line or 'No IPs found' in line:
                    continue
                    
                # جمع البيانات
                if '@' in line and current_section == 'emails':
                    emails.append(line)
                elif current_section == 'hosts' and '.' in line and not line.startswith('Read'):
                    hosts.append(line)
                elif current_section == 'ips' and any(c.isdigit() for c in line):
                    ips.append(line)
            
            # إنشاء نتائج للإيميلات
            for email in emails:
                OSINTResult.objects.create(
                    session=self.session,
                    result_type='email',
                    title=f"بريد إلكتروني: {email}",
                    description=f"تم اكتشاف البريد الإلكتروني من النطاق {self.target}",
                    raw_data={'email': email, 'domain': self.target},
                    confidence='high',
                    confidence_score=0.8,
                    source=self.tool.name,
                    tags=['domain', 'email', 'harvester'],
                    metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                )
            
            # إنشاء نتائج للمضيفين
            for host in hosts:
                OSINTResult.objects.create(
                    session=self.session,
                    result_type='domain',
                    title=f"مضيف: {host}",
                    description=f"تم اكتشاف المضيف من النطاق {self.target}",
                    raw_data={'host': host, 'domain': self.target},
                    confidence='high',
                    confidence_score=0.8,
                    source=self.tool.name,
                    tags=['domain', 'subdomain', 'harvester'],
                    metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                )
            
            # إنشاء نتائج لعناوين IP
            for ip in ips:
                OSINTResult.objects.create(
                    session=self.session,
                    result_type='ip',
                    title=f"عنوان IP: {ip}",
                    description=f"تم اكتشاف عنوان IP من النطاق {self.target}",
                    raw_data={'ip': ip, 'domain': self.target},
                    confidence='high',
                    confidence_score=0.8,
                    source=self.tool.name,
                    tags=['domain', 'ip', 'harvester'],
                    metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                )
            
            # إذا لم نجد أي نتائج، أنشئ نتيجة تفيد بذلك
            if not emails and not hosts and not ips:
                logger.info(f"لم يتم العثور على نتائج في المخرجات: {output_clean[:200]}")
                OSINTResult.objects.create(
                    session=self.session,
                    result_type='domain',
                    title=f"فحص النطاق: {self.target}",
                    description="تم فحص النطاق ولكن لم يتم العثور على معلومات (emails, hosts, IPs)",
                    raw_data={'raw_output': output_clean[:1000], 'target': self.target},
                    confidence='low',
                    confidence_score=0.3,
                    source=self.tool.name,
                    tags=['domain', 'no_results'],
                    metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                )
            else:
                logger.info(f"تم العثور على: {len(emails)} emails, {len(hosts)} hosts, {len(ips)} IPs")
    
    def _process_ip_results(self, output):
        """معالجة نتائج عنوان IP"""
        try:
            data = json.loads(output)
            
            if isinstance(data, dict):
                desc = data.get('description') or data.get('message') or self._generate_summary(data)
                OSINTResult.objects.create(
                    session=self.session,
                    result_type='ip',
                    title=f"معلومات IP: {self.target}",
                    description=desc,
                    url=data.get('url', ''),
                    raw_data=data,
                    confidence='high',
                    confidence_score=0.8,
                    source=self.tool.name,
                    tags=['ip', 'geolocation', 'whois'],
                    metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                )
                
        except json.JSONDecodeError:
            # معالجة النص العادي
            OSINTResult.objects.create(
                session=self.session,
                result_type='ip',
                title=f"معلومات IP: {self.target}",
                description=output.strip(),
                raw_data={'raw_output': output.strip()},
                confidence='medium',
                confidence_score=0.5,
                source=self.tool.name,
                tags=['ip', 'raw'],
                metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
            )
    
    def _process_general_results(self, output):
        """معالجة النتائج العامة"""
        # تجاهل رسائل الإعدادات والرسائل غير المفيدة
        ignore_patterns = [
            'Created default',
            'proxies.yaml',
            'config.yaml',
            'No results found',
            'لم يتم العثور على نتائج',
            'Usage:',
            'usage:',
        ]
        
        output_clean = output.strip()
        
        # تحقق إذا كانت الرسالة يجب تجاهلها
        should_ignore = any(pattern in output_clean for pattern in ignore_patterns)
        
        if should_ignore or len(output_clean) < 10:
            # لا تنشئ نتيجة للرسائل غير المفيدة
            logger.info(f"تجاهل رسالة غير مفيدة: {output_clean[:100]}")
            return
        
        # محاولة تحليل JSON أولاً
        try:
            data = json.loads(output_clean)
            if isinstance(data, dict):
                desc = data.get('description') or data.get('message') or self._generate_summary(data)
                raw_title = f"نتيجة من {self.tool.name}"
                OSINTResult.objects.create(
                    session=self.session,
                    result_type='other',
                    title=raw_title,
                    description=desc,
                    raw_data=data,
                    confidence='high' if data.get('success', True) else 'medium',
                    confidence_score=0.8,
                    source=self.tool.name,
                    tags=['general', 'json'],
                    metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                )
                return
        except json.JSONDecodeError:
            pass

        raw_title = f"نتيجة من {self.tool.name}"
        OSINTResult.objects.create(
            session=self.session,
            result_type='other',
            title=raw_title,
            description=output_clean[:200] + ('...' if len(output_clean) > 200 else ''),
            raw_data={'raw_output': output_clean},
            confidence='medium',
            confidence_score=0.5,
            source=self.tool.name,
            tags=['general', 'raw'],
            metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
        )


class ReportGenerator:
    """فئة لإنشاء التقارير"""
    
    def __init__(self, report):
        self.report = report
        self.session = report.session
        self.results = OSINTResult.objects.filter(session=self.session)
        
    def generate(self):
        """إنشاء التقرير"""
        try:
            if self.report.format == 'html':
                self._generate_html_report()
            elif self.report.format == 'json':
                self._generate_json_report()
            elif self.report.format == 'csv':
                self._generate_csv_report()
            elif self.report.format == 'pdf':
                self._generate_pdf_report()
            
            # تحديث حجم الملف
            if self.report.file:
                self.report.file_size = self.report.file.size
                self.report.save(update_fields=['file_size'])
                
        except Exception as e:
            logger.error(f"خطأ في إنشاء التقرير: {e}")
            raise
    
    def _generate_html_report(self):
        """إنشاء تقرير HTML"""
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{self.report.title}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; }}
                .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .result {{ border: 1px solid #dee2e6; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .confidence-high {{ border-left: 4px solid #28a745; }}
                .confidence-medium {{ border-left: 4px solid #ffc107; }}
                .confidence-low {{ border-left: 4px solid #dc3545; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{self.report.title}</h1>
                <p><strong>الأداة:</strong> {self.session.tool.name}</p>
                <p><strong>الهدف:</strong> {self.session.target}</p>
                <p><strong>تاريخ الإنشاء:</strong> {self.report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>عدد النتائج:</strong> {self.results.count()}</p>
            </div>
            
            <div class="summary">
                <h2>ملخص النتائج</h2>
                <p>{self.report.summary or 'لا يوجد ملخص متاح'}</p>
            </div>
            
            <div class="results">
                <h2>النتائج المكتشفة</h2>
        """
        
        for result in self.results:
            confidence_class = f"confidence-{result.confidence}"
            html_content += f"""
                <div class="result {confidence_class}">
                    <h3>{result.title}</h3>
                    <p><strong>النوع:</strong> {result.result_type}</p>
                    <p><strong>مستوى الثقة:</strong> {result.confidence}</p>
                    <p><strong>المصدر:</strong> {result.source}</p>
                    <p><strong>الوصف:</strong> {result.description}</p>
                    {f'<p><strong>الرابط:</strong> <a href="{result.url}" target="_blank">{result.url}</a></p>' if result.url else ''}
                    <p><strong>تاريخ الاكتشاف:</strong> {result.discovered_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            """
        
        html_content += """
            </div>
            
            <div class="recommendations">
                <h2>التوصيات</h2>
                <p>""" + (self.report.recommendations or 'لا توجد توصيات متاحة') + """</p>
            </div>
        </body>
        </html>
        """
        
        # حفظ الملف
        from django.core.files.base import ContentFile
        self.report.file.save(
            f"report_{self.report.id}.html",
            ContentFile(html_content.encode('utf-8'))
        )
    
    def _generate_json_report(self):
        """إنشاء تقرير JSON"""
        report_data = {
            'report': {
                'id': self.report.id,
                'title': self.report.title,
                'report_type': self.report.report_type,
                'format': self.report.format,
                'generated_at': self.report.generated_at.isoformat(),
                'summary': self.report.summary,
                'recommendations': self.report.recommendations,
            },
            'session': {
                'id': self.session.id,
                'tool': self.session.tool.name,
                'target': self.session.target,
                'status': self.session.status,
                'created_at': self.session.created_at.isoformat(),
                'completed_at': self.session.completed_at.isoformat() if self.session.completed_at else None,
            },
            'results': [
                {
                    'id': result.id,
                    'type': result.result_type,
                    'title': result.title,
                    'description': result.description,
                    'url': result.url,
                    'confidence': result.confidence,
                    'confidence_score': result.confidence_score,
                    'source': result.source,
                    'tags': result.tags,
                    'discovered_at': result.discovered_at.isoformat(),
                    'raw_data': result.raw_data if self.report.include_raw_data else None,
                    'metadata': result.metadata if self.report.include_metadata else None,
                }
                for result in self.results
            ]
        }
        
        # حفظ الملف
        from django.core.files.base import ContentFile
        json_content = json.dumps(report_data, ensure_ascii=False, indent=2)
        self.report.file.save(
            f"report_{self.report.id}.json",
            ContentFile(json_content.encode('utf-8'))
        )
    
    def _generate_csv_report(self):
        """إنشاء تقرير CSV"""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # كتابة العنوان
        writer.writerow([
            'ID', 'النوع', 'العنوان', 'الوصف', 'الرابط', 'الثقة', 'درجة الثقة',
            'المصدر', 'العلامات', 'تاريخ الاكتشاف'
        ])
        
        # كتابة البيانات
        for result in self.results:
            writer.writerow([
                result.id,
                result.result_type,
                result.title,
                result.description,
                result.url,
                result.confidence,
                result.confidence_score,
                result.source,
                ', '.join(result.tags),
                result.discovered_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # حفظ الملف
        from django.core.files.base import ContentFile
        csv_content = output.getvalue()
        self.report.file.save(
            f"report_{self.report.id}.csv",
            ContentFile(csv_content.encode('utf-8'))
        )
    
    def _generate_pdf_report(self):
        """إنشاء تقرير PDF"""
        # هذا يتطلب مكتبة مثل reportlab أو weasyprint
        # للتبسيط، سنقوم بإنشاء HTML أولاً ثم تحويله
        self._generate_html_report()
        
        # يمكن إضافة تحويل HTML إلى PDF هنا
        # باستخدام مكتبات مثل weasyprint أو wkhtmltopdf
