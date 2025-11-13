import subprocess
import json
import os
import logging
import time
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from .models import OSINTSession, OSINTResult, OSINTReport, OSINTActivityLog

logger = logging.getLogger(__name__)


class OSINTToolRunner:
    """فئة لتشغيل أدوات OSINT"""
    
    def __init__(self, session):
        self.session = session
        self.tool = session.tool
        self.target = session.target
        self.config = session.config
        self.options = session.options
        
    def run(self):
        """تشغيل الأداة"""
        try:
            logger.info(f"بدء تشغيل الأداة {self.tool.name} للهدف {self.target}")
            
            # تحديث حالة الجلسة
            self.session.status = 'running'
            self.session.progress = 10
            self.session.current_step = 'جاري التهيئة...'
            self.session.started_at = timezone.now()
            self.session.save()
            
            # بناء الأمر
            command = self._build_command()
            logger.info(f"الأمر: {' '.join(command)}")
            
            # تحديث التقدم
            self.session.progress = 30
            self.session.current_step = 'جاري تشغيل الأداة...'
            self.session.save()
            
            # تشغيل الأداة
            result = self._execute_command(command)
            
            # تحديث التقدم
            self.session.progress = 70
            self.session.current_step = 'جاري معالجة النتائج...'
            self.session.save()
            
            # معالجة النتائج
            self._process_results(result)
            
            # تحديث حالة الجلسة
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
        tool_path = os.path.join(settings.BASE_DIR, 'open_tool', self.tool.tool_path)
        executable = os.path.join(tool_path, self.tool.executable_name)
        
        # استبدال المتغيرات في قالب الأمر
        command_template = self.tool.command_template
        command = command_template.format(
            target=self.target,
            tool_path=tool_path,
            executable=executable,
            **self.config
        )
        
        return command.split()
    
    def _execute_command(self, command):
        """تنفيذ الأمر"""
        try:
            # تغيير المجلد إلى مجلد الأداة
            tool_path = os.path.join(settings.BASE_DIR, 'open_tool', self.tool.tool_path)
            
            # إضافة معالجة خاصة لأدوات Python 2
            if self.tool.tool_type in ['email', 'username'] and 'python' in command[0]:
                # استخدام Python 2 إذا كان متوفراً، وإلا استخدام Python 3 مع معالجة الأخطاء
                try:
                    result = subprocess.run(
                        command,
                        cwd=tool_path,
                        capture_output=True,
                        text=True,
                        timeout=self.tool.timeout,
                        encoding='utf-8',
                        errors='ignore'
                    )
                except Exception as py3_error:
                    # إذا فشل Python 3، جرب مع Python 2
                    if 'python' in command[0]:
                        command[0] = 'python2'
                    result = subprocess.run(
                        command,
                        cwd=tool_path,
                        capture_output=True,
                        text=True,
                        timeout=self.tool.timeout,
                        encoding='utf-8',
                        errors='ignore'
                    )
            else:
                result = subprocess.run(
                    command,
                    cwd=tool_path,
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
                self._process_general_results(result['stdout'])
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
    
    def _process_email_results(self, output):
        """معالجة نتائج البريد الإلكتروني"""
        try:
            # محاولة تحليل JSON
            if output and output.strip():
                data = json.loads(output)
                
                if isinstance(data, dict):
                    # إنشاء نتيجة واحدة
                    OSINTResult.objects.create(
                        session=self.session,
                        result_type='email',
                        title=f"معلومات البريد الإلكتروني: {self.target}",
                        description=data.get('message', 'تم جمع معلومات البريد الإلكتروني'),
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
            # معالجة النص العادي
            if output and output.strip():
                lines = output.strip().split('\n')
                for line in lines:
                    if line.strip() and ':' in line:
                        platform, url = line.split(':', 1)
                        OSINTResult.objects.create(
                            session=self.session,
                            result_type='social_media',
                            title=f"حساب {platform.strip()}: {self.target}",
                            description=f"تم العثور على حساب في {platform.strip()}",
                            url=url.strip(),
                            raw_data={'raw_output': line.strip()},
                            confidence='medium',
                            confidence_score=0.6,
                            source=self.tool.name,
                            tags=['username', 'social_media', platform.strip()],
                            metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                        )
            else:
                # إنشاء نتيجة افتراضية
                OSINTResult.objects.create(
                    session=self.session,
                    result_type='username',
                    title=f"فحص اسم المستخدم: {self.target}",
                    description="تم فحص اسم المستخدم",
                    raw_data={'raw_output': 'No output'},
                    confidence='low',
                    confidence_score=0.3,
                    source=self.tool.name,
                    tags=['username', 'default'],
                    metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                )
    
    def _process_domain_results(self, output):
        """معالجة نتائج النطاق"""
        try:
            data = json.loads(output)
            
            if isinstance(data, dict):
                OSINTResult.objects.create(
                    session=self.session,
                    result_type='domain',
                    title=f"معلومات النطاق: {self.target}",
                    description=data.get('description', ''),
                    url=data.get('url', ''),
                    raw_data=data,
                    confidence='high',
                    confidence_score=0.8,
                    source=self.tool.name,
                    tags=['domain', 'whois', 'dns'],
                    metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
                )
                
        except json.JSONDecodeError:
            # معالجة النص العادي
            OSINTResult.objects.create(
                session=self.session,
                result_type='domain',
                title=f"معلومات النطاق: {self.target}",
                description=output.strip(),
                raw_data={'raw_output': output.strip()},
                confidence='medium',
                confidence_score=0.5,
                source=self.tool.name,
                tags=['domain', 'raw'],
                metadata={'tool': self.tool.name, 'processed_at': timezone.now().isoformat()}
            )
    
    def _process_ip_results(self, output):
        """معالجة نتائج عنوان IP"""
        try:
            data = json.loads(output)
            
            if isinstance(data, dict):
                OSINTResult.objects.create(
                    session=self.session,
                    result_type='ip',
                    title=f"معلومات IP: {self.target}",
                    description=data.get('description', ''),
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
        OSINTResult.objects.create(
            session=self.session,
            result_type='other',
            title=f"نتيجة من {self.tool.name}",
            description=output.strip(),
            raw_data={'raw_output': output.strip()},
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
