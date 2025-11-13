# خريطة المسارات (HTML و API)

هذا المستند يوضح أهم المسارات في منصة Coriza OSINT ويعطي وصفًا موجزًا لكل مسار لتسهيل التطوير والصيانة.

## مسارات الواجهة (HTML)

| المسار | الاسم (namespace:name) | الوصف |
|--------|------------------------|-------|
| `/` | `main:home` | الصفحة الرئيسية، تعرض أحدث المقالات والمحتوى المميز. |
| `/posts/` | `main:posts_list` | قائمة بجميع المقالات المتاحة مع خيارات التصفية والبحث. |
| `/post/<slug>/` | `main:post_detail` | عرض تفاصيل المقال بما في ذلك التعليقات والوسوم. |
| `/contact/` | `main:contact` | نموذج التواصل مع فريق المنصة. |
| `/newsletter/subscribe/` | `main:newsletter_subscribe` | الاشتراك في النشرة البريدية. |
| `/about/` | `main:about` | صفحة "من نحن". |
| `/privacy-policy/` | `main:privacy_policy` | سياسة الخصوصية. |
| `/terms-of-service/` | `main:terms_of_service` | شروط الاستخدام. |
| `/search/` | `main:search` | البحث عن المقالات. |
| `/category/<slug>/` | `main:category_posts` | المقالات ضمن فئة معينة. |
| `/tag/<slug>/` | `main:tag_posts` | المقالات المرتبطة بوسم محدد. |
| `/author/<username>/` | `main:author_posts` | المقالات التي كتبها مؤلف معين. |

### المصادقة

| المسار | الاسم | الوصف |
|--------|-------|-------|
| `/auth/register/` | `authentication:register` | تسجيل مستخدم جديد مع تحقق بالبريد. |
| `/auth/login/` | `authentication:login` | تسجيل الدخول. |
| `/auth/logout/` | `authentication:logout` | تسجيل الخروج. |
| `/auth/profile/` | `authentication:profile` | إدارة الملف الشخصي. |
| `/auth/verify-email/<token>/` | `authentication:verify_email` | التحقق من البريد الإلكتروني. |
| `/auth/password-reset/` | `authentication:password_reset` | طلب إعادة تعيين كلمة المرور. |
| `/auth/password-reset/confirm/<token>/` | `authentication:password_reset_confirm` | إتمام إعادة تعيين كلمة المرور. |

### لوحة التحكم

| المسار | الاسم | الوصف |
|--------|-------|-------|
| `/dashboard/` | `dashboard:index` | لوحة التحكم الرئيسية مع الإحصاءات. |
| `/dashboard/posts/` | `dashboard:posts_management` | إدارة المقالات الخاصة بالمستخدم. |
| `/dashboard/analytics/` | `dashboard:analytics` | التحليلات والرسوم البيانية. |
| `/dashboard/reports/` | `dashboard:reports` | التقارير والملفات الاستخباراتية. |
| `/dashboard/notifications/` | `dashboard:notifications` | مركز الإشعارات مع إمكانية التعليم كمقروء. |
| `/dashboard/activity-log/` | `dashboard:activity_log` | سجل الأنشطة. |
| `/dashboard/settings/` | `dashboard:settings` | إعدادات الحساب. |
| `/dashboard/profile/` | `dashboard:profile` | إدارة الملف الشخصي من لوحة التحكم. |
| `/dashboard/security/` | `dashboard:security` | إعدادات الأمان وإدارة الجلسات. |

### أدوات OSINT (واجهة HTML)

| المسار | الاسم | الوصف |
|--------|-------|-------|
| `/osint/` | `osint_tools:dashboard` | لوحة تحكم أدوات OSINT. |
| `/osint/tools/` | `osint_tools:tools_list` | قائمة بجميع الأدوات المتاحة. |
| `/osint/tools/<tool_slug>/` | `osint_tools:tool_detail` | تفاصيل الأداة وإعداداتها. |
| `/osint/tools/<tool_slug>/run/` | `osint_tools:run_tool` | تشغيل الأداة على هدف محدد. |
| `/osint/tools/<tool_slug>/test/` | `osint_tools:test_tool` | اختبار الأداة والتحقق من جاهزيتها. |
| `/osint/sessions/` | `osint_tools:sessions_list` | قائمة الجلسات السابقة. |
| `/osint/sessions/<id>/` | `osint_tools:session_detail` | تفاصيل جلسة معينة. |
| `/osint/results/` | `osint_tools:results_list` | النتائج المكتشفة. |
| `/osint/reports/` | `osint_tools:reports_list` | التقارير المولدة. |
| `/osint/configurations/` | `osint_tools:configurations_list` | إعدادات الأدوات والجلسات. |
| `/osint/analytics/` | `osint_tools:analytics` | تحليلات استخدام أدوات OSINT. |

## مسارات REST API

### الجذر
- `/api/` → وثائق API أو نظرة عامة.
- `/api/v1/` → نقطة الدخول للإصدار الأول.

### المستخدمون
| المسار | الوصف |
|--------|-------|
| `/api/v1/users/` | قائمة المستخدمين (مصادقة مطلوبة). |
| `/api/v1/users/<username>/` | تفاصيل مستخدم محدد. |

### المنشورات والمحتوى
| المسار | الوصف |
|--------|-------|
| `/api/v1/posts/` | قائمة المنشورات (يدعم الترشيح والبحث). |
| `/api/v1/posts/<slug>/` | تفاصيل منشور. |
| `/api/v1/categories/` | قائمة الفئات. |
| `/api/v1/categories/<slug>/` | تفاصيل فئة. |
| `/api/v1/comments/` | قائمة التعليقات. |
| `/api/v1/comments/<id>/` | تفاصيل/تحديث تعليق. |

### إدارة API و Webhooks
| المسار | الوصف |
|--------|-------|
| `/api/v1/keys/` | إدارة مفاتيح API. |
| `/api/v1/keys/<id>/` | تفاصيل مفتاح. |
| `/api/v1/webhooks/` | إدارة Webhooks. |
| `/api/v1/webhooks/<id>/` | تفاصيل Webhook. |
| `/api/v1/webhooks/<id>/test/` | اختبار Webhook. |

### معلومات API
| المسار | الوصف |
|--------|-------|
| `/api/v1/versions/` | إصدارات API المتاحة. |
| `/api/v1/endpoints/` | قائمة نقاط النهاية الموثقة. |
| `/api/v1/stats/` | إحصاءات الاستخدام. |
| `/api/v1/documentation/` | مستند الوثائق (HTML/JSON). |

### API لأدوات OSINT (داخل `/osint/api/`)
| المسار | الوصف |
|--------|-------|
| `/osint/api/tools/` | CRUD للأدوات (ViewSet). |
| `/osint/api/sessions/` | CRUD للجلسات. |
| `/osint/api/results/` | CRUD للنتائج. |
| `/osint/api/reports/` | CRUD للتقارير. |
| `/osint/api/configurations/` | إدارة الإعدادات. |
| `/osint/api/stats/` | إحصاءات عامة للأدوات. |
| `/osint/api/tools/<slug>/test/` | اختبار أداة عبر API. |

---
> **ملاحظة:** معظم المسارات تتطلب مصادقة (Session أو Token) حسب إعدادات Django REST Framework.
