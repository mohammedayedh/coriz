# 🔄 دورة حياة البيانات في منصة Coriza OSINT - مخططات مرئية

## 📊 المخطط الشامل لدورة حياة البيانات

```
╔══════════════════════════════════════════════════════════════════╗
║           COMPLETE DATA LIFECYCLE IN CORIZA OSINT                ║
╚══════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: DATA CREATION (إنشاء البيانات)                         │
├─────────────────────────────────────────────────────────────────┤
│ Input: User Request (POST /osint/tools/sherlock/run/)           │
│ Process:                                                        │
│   1. Extract data from request body                             │
│   2. Create OSINTSession object                                 │
│   3. Create OSINTActivityLog entry                              │
│ Output: session_id, task_id                                     │
│ Database Tables: osint_tools_osintsession,                      │
│                  osint_tools_osintactivitylog                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ PHASE 2: DATA VALIDATION (التحقق من صحة البيانات)              │
├────────────────────────────────────────────────────────────────┤
│ Checks:                                                        │
│   ✓ User authentication (is_authenticated)                     │
│   ✓ User clearance level (L1-L4)                               │
│   ✓ Tool clearance requirement                                 │
│   ✓ Rate limiting (cache check)                                │
│   ✓ Input validation (target format)                           │
│   ✓ JSON fields validation (JSONValidationMixin)               │
│ Result: PASS → Continue | FAIL → Return Error                  │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: DATA STORAGE (تخزين البيانات)                          │
├─────────────────────────────────────────────────────────────────┤
│ Storage Locations:                                              │
│   1. PostgreSQL/SQLite:                                         │
│      - OSINTSession (status='pending')                          │
│      - OSINTActivityLog                                         │
│   2. Redis:                                                     │
│      - Celery task queue                                        │
│      - Rate limit counters                                      │
│      - Session cache                                            │
│ Timestamps: created_at, updated_at                              │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 4: DATA PROCESSING (معالجة البيانات)                      │
├─────────────────────────────────────────────────────────────────┤
│ Celery Worker:                                                  │
│   1. Fetch task from Redis queue                                │
│   2. Update session status → 'running'                          │
│   3. Execute OSINTToolRunner.run()                              │
│      a. Build command                                           │
│      b. Execute subprocess                                      │
│      c. Parse output (JSON/Text)                                │
│      d. Create OSINTResult objects                              │
│   4. Update session status → 'completed'/'failed'               │
│ Progress Updates: 0% → 10% → 30% → 70% → 100%                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 5: DATA ANALYSIS (تحليل البيانات)                         │
├─────────────────────────────────────────────────────────────────┤
│ Analysis Operations:                                             │
│   1. Count results by type                                      │
│   2. Calculate confidence distribution                          │
│   3. Generate results_summary (JSON)                            │
│   4. Update session.results_count                               │
│   5. Calculate success metrics                                  │
│ Output: Structured analytics data                               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 6: DATA PRESENTATION (عرض البيانات)                      │
├─────────────────────────────────────────────────────────────────┤
│ Presentation Methods:                                            │
│   1. Web UI:                                                    │
│      - Session detail page                                      │
│      - Results list with filters                                │
│      - Charts and graphs                                        │
│   2. REST API:                                                  │
│      - GET /osint/api/sessions/{id}/                            │
│      - GET /osint/api/results/?session={id}                     │
│   3. Reports:                                                   │
│      - HTML, PDF, JSON, CSV formats                             │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 7: DATA ARCHIVING (أرشفة البيانات)                       │
├─────────────────────────────────────────────────────────────────┤
│ Archiving Options:                                               │
│   1. Export to JSON (full data)                                │
│   2. Export to CSV (tabular data)                               │
│   3. Generate PDF report                                        │
│   4. Store report files in media/osint_reports/                │
│ Metadata: file_size, generated_at, downloaded_count            │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 8: DATA DELETION (حذف البيانات)                          │
├─────────────────────────────────────────────────────────────────┤
│ Deletion Cascade:                                                │
│   OSINTSession.delete() triggers:                               │
│     → Delete all OSINTResult (CASCADE)                          │
│     → Delete all OSINTReport (CASCADE)                          │
│     → Delete all OSINTActivityLog (SET_NULL)                    │
│     → Delete report files from filesystem                       │
│     → Delete log files from filesystem                          │
│ Soft Delete Option: status='archived' (not implemented)        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 تتبع بيانات جلسة واحدة (Single Session Data Tracking)

```
Session ID: 123
Target: "john_doe"
Tool: "Sherlock"
User: user@example.com (Clearance: L2)

Timeline:
─────────────────────────────────────────────────────────────────

T+0s    [CREATE]
        ├─ OSINTSession created (status='pending')
        ├─ OSINTActivityLog: 'tool_run'
        └─ Celery task queued

T+2s    [VALIDATE]
        ├─ Check user clearance: L2 >= L1 ✓
        ├─ Check rate limit: 3/100 ✓
        └─ Validate target: "john_doe" ✓

T+3s    [STORE]
        ├─ Database: INSERT INTO osint_tools_osintsession
        ├─ Redis: LPUSH celery:queue:osint_tools
        └─ Cache: SET rate_limit:192.168.1.1 = 4

T+5s    [PROCESS - START]
        ├─ Celery worker picks task
        ├─ Update: status='running', progress=10
        └─ OSINTActivityLog: 'session_started'

T+10s   [PROCESS - EXECUTE]
        ├─ Build command: ['python', 'sherlock.py', 'john_doe']
        ├─ Execute subprocess
        ├─ Update: progress=30, current_step='جاري التشغيل...'
        └─ Capture output

T+45s   [PROCESS - PARSE]
        ├─ Parse JSON output
        ├─ Create 45 OSINTResult objects
        ├─ Update: progress=70, results_count=45
        └─ OSINTActivityLog: 'results_found'

T+50s   [PROCESS - COMPLETE]
        ├─ Update: status='completed', progress=100
        ├─ Calculate duration: 45 seconds
        ├─ Update: completed_at, duration
        └─ OSINTActivityLog: 'session_completed'

T+60s   [ANALYZE]
        ├─ Count by type: {social_media: 40, profile: 5}
        ├─ Count by confidence: {high: 35, medium: 8, low: 2}
        ├─ Update: results_summary (JSON)
        └─ Calculate success_rate: 95%

T+120s  [PRESENT]
        ├─ User views session detail page
        ├─ Display 45 results with pagination
        └─ Show charts and statistics

T+300s  [ARCHIVE]
        ├─ User requests HTML report
        ├─ Generate report (Celery task)
        ├─ Save to: media/osint_reports/report_456.html
        └─ Update: OSINTReport (status='completed')

T+600s  [DOWNLOAD]
        ├─ User downloads report
        ├─ Update: downloaded_count += 1
        └─ OSINTActivityLog: 'report_downloaded'

T+∞     [DELETE] (Optional)
        ├─ User deletes session
        ├─ CASCADE delete 45 OSINTResult
        ├─ CASCADE delete 1 OSINTReport
        ├─ Delete report file from filesystem
        └─ SET_NULL OSINTActivityLog.session_id
```

---

## 📈 تدفق البيانات عبر الطبقات

```
┌──────────────────────────────────────────────────────────────┐
│                    LAYER-BY-LAYER DATA FLOW                   │
└──────────────────────────────────────────────────────────────┘

[Presentation Layer]
    ↓ HTTP Request (JSON)
    {
        "target": "john_doe",
        "tool": 1,
        "case_id": 5
    }
    ↓
[Application Layer - View]
    ↓ Python Object
    session = OSINTSession(
        user=request.user,
        tool=tool,
        target="john_doe",
        status='pending'
    )
    ↓
[Business Logic Layer - Model]
    ↓ Validation
    session.full_clean()  # JSONValidationMixin
    ↓
[Data Access Layer - ORM]
    ↓ SQL Query
    INSERT INTO osint_tools_osintsession
    (user_id, tool_id, target, status, created_at)
    VALUES (1, 1, 'john_doe', 'pending', '2026-04-17 10:30:00')
    ↓
[Database Layer]
    ↓ Storage
    PostgreSQL Table: osint_tools_osintsession
    Row ID: 123
    ↓
[Cache Layer]
    ↓ Redis
    SET session:123 = {serialized_data}
    EXPIRE session:123 3600
    ↓
[Message Queue]
    ↓ Celery
    LPUSH celery:queue:osint_tools
    {task_id, session_id, args}
    ↓
[Worker Layer]
    ↓ Processing
    run_osint_tool(session_id=123)
    ↓
[External Tool]
    ↓ Subprocess
    python sherlock.py john_doe --json
    ↓
[Output Parsing]
    ↓ JSON
    {
        "results": [
            {"platform": "Twitter", "found": true},
            {"platform": "GitHub", "found": true}
        ]
    }
    ↓
[Result Storage]
    ↓ Multiple INSERTs
    INSERT INTO osint_tools_osintresult × 45
    ↓
[Update Session]
    ↓ UPDATE
    UPDATE osint_tools_osintsession
    SET status='completed', results_count=45
    WHERE id=123
    ↓
[Response to User]
    ↓ HTTP Response (JSON)
    {
        "success": true,
        "session_id": 123,
        "status": "completed",
        "results_count": 45
    }
```

---

## 🗄️ حالات البيانات (Data States)

```
OSINTSession States:
┌─────────┐
│ pending │ ← Initial state
└────┬────┘
     │ Celery picks task
     ↓
┌─────────┐
│ running │ ← Processing
└────┬────┘
     │ Success?
     ├─ Yes → ┌───────────┐
     │         │ completed │ ← Final state (success)
     │         └───────────┘
     │
     └─ No  → ┌─────────┐
               │ failed  │ ← Final state (error)
               └─────────┘

Manual intervention:
┌───────────┐
│ cancelled │ ← User cancels
└───────────┘
```

---

