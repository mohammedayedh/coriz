## 5. التطبيقات (Apps) والوظائف

### 5.1 نظرة عامة على التطبيقات

```
coriza/
├── authentication/    # إدارة المستخدمين والمصادقة
├── main/             # الواجهة العامة والمحتوى
├── dashboard/        # لوحة تحكم المستخدمين
├── osint_tools/      # محرك أدوات OSINT (القلب)
└── api/              # واجهات REST API
```

---

### 5.2 تطبيق Authentication (المصادقة)

#### 5.2.1 الوظائف الرئيسية

**1. التسجيل (Registration)**
```python
# views.py - register_view()
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # إنشاء المستخدم
            user = form.save(commit=False)
            user.is_verified = False
            user.save()
            
            # إنشاء الملف الشخصي
            UserProfile.objects.create(
                user=user,
                clearance_level='L1'  # المستوى الافتراضي
            )
            
            # إرسال بريد التحقق
            token = secrets.token_urlsafe(32)
            EmailVerification.objects.create(
                user=user,
                token=token,
                expires_at=timezone.now() + timedelta(hours=24)
            )
            send_verification_email(user, token)
```

**دورة حياة التسجيل:**
```
1. المستخدم يملأ النموذج
   ↓
2. التحقق من صحة البيانات (Validation)
   - البريد فريد؟
   - اسم المستخدم فريد؟
   - كلمة المرور قوية؟
   ↓
3. إنشاء User + UserProfile
   ↓
4. إنشاء EmailVerification token
   ↓
5. إرسال بريد التحقق
   ↓
6. المستخدم يضغط على الرابط
   ↓
7. تفعيل الحساب (is_verified = True)
```

**2. تسجيل الدخول (Login)**
```python
# views.py - login_view()
def login_view(request):
    # التحقق من Rate Limiting
    if is_rate_limited('login', get_client_ip(request)):
        return JsonResponse({'error': 'تجاوزت الحد المسموح'}, status=429)
    
    # المصادقة
    user = authenticate(email=email, password=password)
    
    if user:
        # تسجيل محاولة ناجحة
        LoginAttempt.objects.create(
            user=user,
            email=email,
            ip_address=get_client_ip(request),
            success=True
        )
        
        # تسجيل الدخول
        login(request, user)
        
        # إنشاء جلسة
        UserSession.objects.create(
            user=user,
            session_key=request.session.session_key,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
    else:
        # تسجيل محاولة فاشلة
        LoginAttempt.objects.create(
            email=email,
            ip_address=get_client_ip(request),
            success=False
        )
        incr_rate('login', get_client_ip(request))
```

**3. التحقق من البريد (Email Verification)**
```python
# views.py - verify_email_view()
def verify_email_view(request, token):
    try:
        verification = EmailVerification.objects.get(
            token=token,
            is_used=False
        )
        
        if verification.is_expired():
            return render(request, 'authentication/verification_expired.html')
        
        # تفعيل الحساب
        user = verification.user
        user.is_verified = True
        user.save()
        
        # تعليم الرمز كمستخدم
        verification.is_used = True
        verification.save()
        
        messages.success(request, 'تم تفعيل حسابك بنجاح!')
        return redirect('authentication:login')
        
    except EmailVerification.DoesNotExist:
        return render(request, 'authentication/verification_invalid.html')
```

**4. إعادة تعيين كلمة المرور (Password Reset)**
```python
# دورة حياة إعادة التعيين:
1. المستخدم يطلب إعادة التعيين
   ↓
2. إنشاء PasswordReset token
   ↓
3. إرسال بريد مع الرابط
   ↓
4. المستخدم يضغط على الرابط
   ↓
5. التحقق من صلاحية الرمز
   ↓
6. إدخال كلمة المرور الجديدة
   ↓
7. تحديث كلمة المرور
   ↓
8. تعليم الرمز كمستخدم
```

#### 5.2.2 نظام Rate Limiting

```python
RATE_LIMITS = {
    'login': {'limit': 5, 'window': 15 * 60},  # 5 محاولات كل 15 دقيقة
    'password_reset': {'limit': 5, 'window': 15 * 60},
    'resend_verification': {'limit': 5, 'window': 15 * 60},
}

def is_rate_limited(kind: str, ident: str) -> bool:
    """التحقق من تجاوز الحد"""
    conf = RATE_LIMITS[kind]
    key = f"auth:{kind}:{ident}"
    count = cache.get(key, 0)
    return count >= conf['limit']

def incr_rate(kind: str, ident: str):
    """زيادة العداد"""
    conf = RATE_LIMITS[kind]
    key = f"auth:{kind}:{ident}"
    val = cache.get(key, 0)
    if val == 0:
        cache.set(key, 1, timeout=conf['window'])
    else:
        cache.incr(key)
```

---

### 5.3 تطبيق OSINT Tools (المحرك الرئيسي)

#### 5.3.1 هيكل التطبيق

```
osint_tools/
├── models.py           # النماذج (8 نماذج)
├── views.py            # العروض (40+ view)
├── urls.py             # المسارات
├── serializers.py      # المسلسلات (REST)
├── tasks.py            # مهام Celery
├── utils.py            # أدوات مساعدة
├── signals.py          # الإشارات
├── admin.py            # لوحة الإدارة
└── management/
    └── commands/
        └── create_osint_tools.py  # أمر إنشاء الأدوات
```

#### 5.3.2 تدفق تنفيذ أداة OSINT (مفصل)

**الخطوة 1: طلب المستخدم**
```python
# المستخدم يضغط على "Run Tool"
POST /osint/tools/sherlock/run/
{
    "target": "john_doe",
    "case_id": 5,
    "config_id": null,
    "options": {"timeout": 60}
}
```

**الخطوة 2: معالجة الطلب في View**
```python
# views.py - run_tool()
@login_required
def run_tool(request, tool_slug):
    tool = get_object_or_404(OSINTTool, slug=tool_slug)
    
    # 1. التحقق من الصلاحيات
    user_clearance = request.user.profile.clearance_level
    if user_clearance < tool.required_clearance:
        return JsonResponse({'error': 'صلاحيات غير كافية'}, status=403)
    
    # 2. استخراج البيانات
    data = json.loads(request.body)
    target = data.get('target', '').strip()
    case_id = data.get('case_id')
    
    # 3. إنشاء الجلسة
    session = OSINTSession.objects.create(
        user=request.user,
        tool=tool,
        target=target,
        investigation_case=case if case_id else None,
        status='pending'
    )
    
    # 4. تسجيل النشاط
    OSINTActivityLog.objects.create(
        user=request.user,
        session=session,
        action='tool_run',
        description=f'تم جدولة تشغيل أداة {tool.name}',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    # 5. جدولة المهمة في Celery
    task = run_osint_tool.delay(session.id)
    session.celery_task_id = task.id
    session.save()
    
    return JsonResponse({
        'success': True,
        'session_id': session.id,
        'task_id': task.id
    })
```

**الخطوة 3: تنفيذ المهمة في Celery Worker**
```python
# tasks.py - run_osint_tool()
@shared_task(bind=True)
def run_osint_tool(self, session_id):
    # 1. جلب الجلسة
    session = OSINTSession.objects.get(pk=session_id)
    
    # 2. تحديث الحالة
    session.mark_running(task_id=self.request.id)
    
    # 3. إنشاء Runner
    runner = OSINTToolRunner(session)
    
    try:
        # 4. تشغيل الأداة
        runner.run()
        
        # 5. تحديث الحالة
        session.refresh_from_db()
        if session.status == 'running':
            session.mark_completed()
            
    except Exception as exc:
        # 6. معالجة الأخطاء
        session.mark_failed(str(exc))
        
        # 7. تسجيل الخطأ
        OSINTActivityLog.objects.create(
            user=session.user,
            session=session,
            action='error_occurred',
            description=f'Failed to run tool {session.tool.name}',
            details={'error': str(exc)}
        )
        raise
    
    return {'status': session.status, 'session_id': session.id}
```

**الخطوة 4: تنفيذ الأداة (OSINTToolRunner)**
```python
# utils.py - OSINTToolRunner
class OSINTToolRunner:
    def __init__(self, session):
        self.session = session
        self.tool = session.tool
        self.target = session.target
    
    def run(self):
        # 1. تحديث التقدم
        self.session.progress = 10
        self.session.current_step = 'جاري التهيئة...'
        self.session.save()
        
        # 2. بناء الأمر
        command = self._build_command()
        # مثال: ['python', 'sherlock.py', 'john_doe', '--json']
        
        # 3. تحديث التقدم
        self.session.progress = 30
        self.session.current_step = 'جاري تشغيل الأداة...'
        self.session.save()
        
        # 4. تنفيذ الأمر
        result = self._execute_command(command)
        
        # 5. تحديث التقدم
        self.session.progress = 70
        self.session.current_step = 'جاري معالجة النتائج...'
        self.session.save()
        
        # 6. معالجة النتائج
        self._process_results(result)
        
        # 7. تحديث التقدم
        self.session.progress = 100
        self.session.current_step = 'تم الانتهاء بنجاح!'
        self.session.save()
    
    def _build_command(self):
        """بناء أمر التنفيذ"""
        tool_path = os.path.join(settings.BASE_DIR, 'open_tool', self.tool.tool_path)
        executable = os.path.join(tool_path, self.tool.executable_name)
        
        # استبدال المتغيرات في القالب
        command = self.tool.command_template.format(
            target=self.target,
            executable=executable,
            **self.session.config
        )
        
        return command.split()
    
    def _execute_command(self, command):
        """تنفيذ الأمر الخارجي"""
        tool_path = os.path.join(settings.BASE_DIR, 'open_tool', self.tool.tool_path)
        
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
    
    def _process_results(self, result):
        """معالجة مخرجات الأداة"""
        if result['returncode'] != 0:
            raise Exception(f"فشل في تشغيل الأداة: {result['stderr']}")
        
        # معالجة حسب نوع الأداة
        if self.tool.tool_type == 'username':
            self._process_username_results(result['stdout'])
        elif self.tool.tool_type == 'email':
            self._process_email_results(result['stdout'])
        # ... إلخ
    
    def _process_username_results(self, output):
        """معالجة نتائج البحث عن اسم المستخدم"""
        try:
            data = json.loads(output)
            
            # إنشاء نتيجة رئيسية
            OSINTResult.objects.create(
                session=self.session,
                result_type='username',
                title=f"معلومات اسم المستخدم: {self.target}",
                description=data.get('message', 'تم البحث عن اسم المستخدم'),
                raw_data=data,
                confidence='high' if data.get('success') else 'medium',
                source=self.tool.name
            )
            
            # معالجة النتائج الفرعية
            if 'results' in data:
                for item in data['results']:
                    OSINTResult.objects.create(
                        session=self.session,
                        result_type='social_media',
                        title=f"حساب {item.get('platform')}: {self.target}",
                        url=item.get('url', ''),
                        raw_data=item,
                        confidence='high' if item.get('found') else 'low',
                        source=self.tool.name,
                        tags=['username', 'social_media', item.get('platform')]
                    )
            
            # تحديث عدد النتائج
            self.session.results_count = OSINTResult.objects.filter(
                session=self.session
            ).count()
            self.session.save()
            
        except json.JSONDecodeError:
            # معالجة النص العادي
            OSINTResult.objects.create(
                session=self.session,
                result_type='username',
                title=f"نتيجة للبحث: {self.target}",
                description=output.strip(),
                raw_data={'raw_output': output.strip()},
                confidence='low',
                source=self.tool.name
            )
```

**الخطوة 5: تتبع التقدم (Real-time Progress)**
```javascript
// في الواجهة الأمامية
function checkProgress(sessionId) {
    fetch(`/osint/ajax/session-status/${sessionId}/`)
        .then(response => response.json())
        .then(data => {
            // تحديث شريط التقدم
            document.getElementById('progress-bar').style.width = data.progress + '%';
            document.getElementById('current-step').textContent = data.current_step;
            
            // إذا لم تكتمل، استمر في التحقق
            if (data.status === 'running') {
                setTimeout(() => checkProgress(sessionId), 2000);
            } else if (data.status === 'completed') {
                window.location.href = `/osint/sessions/${sessionId}/`;
            }
        });
}
```

#### 5.3.3 نظام التقارير (Report Generation)

```python
# views.py - generate_report()
@login_required
def generate_report(request, session_id):
    session = get_object_or_404(OSINTSession, id=session_id, user=request.user)
    
    data = json.loads(request.body)
    
    # إنشاء التقرير
    report = OSINTReport.objects.create(
        user=request.user,
        session=session,
        title=f"تقرير {session.tool.name} - {session.target}",
        report_type=data.get('report_type', 'summary'),
        format=data.get('format', 'html'),
        include_raw_data=data.get('include_raw_data', False),
        status='pending'
    )
    
    # جدولة توليد التقرير
    task = generate_osint_report.delay(report.id)
    report.celery_task_id = task.id
    report.save()
    
    return JsonResponse({
        'success': True,
        'report_id': report.id
    })
```

```python
# tasks.py - generate_osint_report()
@shared_task(bind=True)
def generate_osint_report(self, report_id):
    report = OSINTReport.objects.get(pk=report_id)
    report.mark_running(task_id=self.request.id)
    
    try:
        generator = ReportGenerator(report)
        generator.generate()
        report.mark_completed()
    except Exception as exc:
        report.mark_failed(str(exc))
        raise
```

```python
# utils.py - ReportGenerator
class ReportGenerator:
    def __init__(self, report):
        self.report = report
        self.session = report.session
        self.results = OSINTResult.objects.filter(session=self.session)
    
    def generate(self):
        if self.report.format == 'html':
            self._generate_html_report()
        elif self.report.format == 'json':
            self._generate_json_report()
        elif self.report.format == 'csv':
            self._generate_csv_report()
    
    def _generate_html_report(self):
        """توليد تقرير HTML"""
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <title>{self.report.title}</title>
            <style>
                body {{ font-family: Arial; }}
                .result {{ border: 1px solid #ddd; padding: 10px; margin: 10px 0; }}
                .confidence-high {{ border-left: 4px solid green; }}
                .confidence-medium {{ border-left: 4px solid orange; }}
                .confidence-low {{ border-left: 4px solid red; }}
            </style>
        </head>
        <body>
            <h1>{self.report.title}</h1>
            <p><strong>الأداة:</strong> {self.session.tool.name}</p>
            <p><strong>الهدف:</strong> {self.session.target}</p>
            <p><strong>عدد النتائج:</strong> {self.results.count()}</p>
            
            <h2>النتائج</h2>
        """
        
        for result in self.results:
            html_content += f"""
            <div class="result confidence-{result.confidence}">
                <h3>{result.title}</h3>
                <p><strong>النوع:</strong> {result.result_type}</p>
                <p><strong>الثقة:</strong> {result.confidence}</p>
                <p>{result.description}</p>
                {f'<a href="{result.url}">{result.url}</a>' if result.url else ''}
            </div>
            """
        
        html_content += "</body></html>"
        
        # حفظ الملف
        self.report.file.save(
            f"report_{self.report.id}.html",
            ContentFile(html_content.encode('utf-8'))
        )
```

---

