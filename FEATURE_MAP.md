# 🗺️ FEATURE MAP & NAVIGATION GUIDE

## 🎯 Quick Navigation

```
┌─────────────────────────────────────────────────────────┐
│         TOXICITY DETECTION SYSTEM - FEATURE MAP         │
│                    http://127.0.0.1:5000                │
└─────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  HOME PAGE                                                   │
│  Route: /                                                    │
│  ├─ Single Message Analysis                                 │
│  ├─ Get AI Suggestions                                      │
│  ├─ View Category Breakdown                                 │
│  └─ See Severity Levels                                     │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  CHAT ANALYZER                                               │
│  Route: /chat-analyzer                                       │
│  ├─ Real-time Message Monitoring                            │
│  ├─ User Behavior Tracking                                  │
│  ├─ Automated Moderation                                    │
│  └─ Export Chat History                                     │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  LIVE DASHBOARD                                              │
│  Route: /live-dashboard                                      │
│  ├─ Real-time Metrics (Auto-refresh: 2s)                    │
│  ├─ 4 Interactive Charts                                    │
│  ├─ Activity Feed                                           │
│  └─ Animated Metric Cards                                   │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  🆕 COMPARISON TOOL                                          │
│  Route: /comparison                                          │
│  ├─ Side-by-Side Message Comparison                         │
│  ├─ Improvement Percentage                                  │
│  ├─ Winner Badge System                                     │
│  └─ Quick Example Templates                                 │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  🆕 ANALYTICS DASHBOARD                                      │
│  Route: /analytics                                           │
│  ├─ 7-Day Trend Charts                                      │
│  ├─ 24-Hour Toxicity Heatmap                                │
│  ├─ Category Distribution                                   │
│  ├─ AI-Generated Insights                                   │
│  └─ Statistical Summary                                     │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  🆕 BATCH ANALYSIS                                           │
│  Route: /batch                                               │
│  ├─ Drag-and-Drop Upload                                    │
│  ├─ Manual Text Input                                       │
│  ├─ Progress Tracking                                       │
│  ├─ Export: CSV / JSON / HTML                               │
│  └─ Summary Statistics                                      │
└──────────────────────────────────────────────────────────────┘
```

---

## 📊 API ENDPOINTS MAP

### Analysis APIs
```
POST /predict
├─ Input: {"text": "message"}
├─ Output: Toxicity analysis
└─ Logged: ✅ Analytics

POST /api/batch-analyze
├─ Input: {"messages": [...]}
├─ Output: Batch results + summary
└─ Logged: ✅ Analytics (each message)

POST /api/chat/moderate
├─ Input: {"text": "msg", "user": "id"}
├─ Output: Moderation + user profile
└─ Tracked: ✅ User behavior
```

### Analytics APIs
```
GET /api/analytics?days=7
├─ Returns: Trends, categories, peak hours
└─ Includes: Statistics + AI insights

GET /api/dashboard/data
├─ Returns: Real-time metrics
└─ Refreshes: Every 30 seconds

GET /api/user-profile/<user_id>
├─ Returns: User behavior profile
└─ Includes: Risk score, patterns, strikes
```

### Export APIs
```
POST /api/export
├─ Input: {"results": [...], "format": "csv|json|html"}
├─ Output: Downloadable file
└─ Formats: CSV, JSON, HTML report
```

### Suggestion APIs
```
POST /api/suggest-alternatives
├─ Input: {"text": "toxic message"}
├─ Output: Rephrasing suggestions
└─ Returns: Multiple alternatives

POST /api/analyze-conversation
├─ Input: {"messages": [...]}
├─ Output: Conversation-level analysis
└─ Includes: Flow analysis
```

---

## 🎯 FEATURE DEPENDENCY MAP

```
Enhanced Toxicity Analyzer (Core)
    ↓
    ├─── Single Analysis (/predict)
    │        ↓
    │        ├─── Home Page
    │        ├─── Chat Analyzer
    │        └─── Comparison Tool
    │
    ├─── Batch Analysis (/api/batch-analyze)
    │        ↓
    │        └─── Batch Upload Page
    │
    ├─── Analytics Logging
    │        ↓
    │        ├─── Analytics Dashboard
    │        └─── Trends & Insights
    │
    ├─── User Behavior Tracking
    │        ↓
    │        ├─── Chat Moderation
    │        └─── User Profiles
    │
    └─── Export System
             ↓
             └─── CSV / JSON / HTML Reports
```

---

## 🎨 UI COMPONENT MAP

### Color System
```
Risk Levels:
🟢 SAFE     (#10b981) - Toxicity < 20
🟡 LOW      (#84cc16) - Toxicity 20-40
🟠 MEDIUM   (#f59e0b) - Toxicity 40-60
🔴 HIGH     (#f97316) - Toxicity 60-80
⛔ SEVERE   (#ef4444) - Toxicity 80-90
🚨 EXTREME  (#dc2626) - Toxicity > 90

Gradients:
🌈 Purple   (#667eea → #764ba2) - Headers, buttons
🌈 Green    (#10b981 → #059669) - Success cards
🌈 Orange   (#f59e0b → #d97706) - Warning cards
🌈 Red      (#ef4444 → #dc2626) - Danger cards
```

### Chart Types
```
Line Charts:
├─ Toxicity trends over time
└─ Dual-axis (score + count)

Doughnut Charts:
├─ Category distribution
└─ Level distribution

Bar Charts:
├─ Comparison metrics
└─ Statistical breakdown

Heatmaps:
├─ 24-hour toxicity grid
└─ Intensity-based coloring
```

---

## 📁 FILE ORGANIZATION MAP

```
d:\spark main\
│
├─ 🔧 Backend Files
│  ├─ app.py                          (Main Flask app)
│  ├─ enhanced_toxicity_analysis.py   (Core analyzer)
│  ├─ analytics_engine.py             (🆕 Analytics)
│  ├─ export_system.py                (🆕 Export)
│  ├─ response_suggestions.py         (AI suggestions)
│  └─ user_behavior_tracker.py        (User tracking)
│
├─ 🎨 Frontend Files
│  ├─ templates/
│  │  ├─ index.html                   (Home)
│  │  ├─ chat_analyzer.html           (Chat)
│  │  ├─ live_dashboard.html          (Dashboard)
│  │  ├─ comparison.html              (🆕 Compare)
│  │  ├─ analytics.html               (🆕 Analytics)
│  │  └─ batch.html                   (🆕 Batch)
│  │
│  └─ static/
│     ├─ style.css                    (Main styles)
│     └─ app.js                       (Frontend logic)
│
├─ 💾 Data Files
│  └─ data/
│     ├─ toxicity_words_database.txt  (2000+ words)
│     ├─ analytics_history.json       (🆕 Auto-created)
│     └─ datasets/
│
├─ 📚 Documentation
│  ├─ README.md                       (Project overview)
│  ├─ NEW_FEATURES_ADDED.md           (🆕 Feature docs)
│  ├─ SETUP_COMPLETE.md               (🆕 Setup guide)
│  ├─ QUICK_REFERENCE.md              (🆕 Quick guide)
│  └─ PROJECT_COMPLETION.md           (🆕 Summary)
│
└─ 🚀 Startup Files
   └─ START_APP.bat                   (⭐ Updated)
```

---

## 🔄 DATA FLOW MAP

### Single Message Flow
```
User Input
   ↓
[POST /predict]
   ↓
Enhanced Toxicity Analyzer
   ├─ Match 2000+ word database
   ├─ Calculate severity (1-5)
   ├─ Categorize (9 categories)
   └─ Generate warning
   ↓
Analytics Logging
   ├─ Save to JSON
   ├─ Update daily stats
   └─ Track patterns
   ↓
Return Results
   ├─ Score (0-100)
   ├─ Level (SAFE-EXTREME)
   ├─ Matched words
   ├─ Category breakdown
   └─ Warning message
```

### Batch Processing Flow
```
File Upload / Manual Input
   ↓
[POST /api/batch-analyze]
   ↓
Parse Messages
   ├─ CSV → Extract text
   ├─ JSON → Parse array
   └─ TXT → Split lines
   ↓
Analyze Each (Export System)
   ├─ Loop through messages
   ├─ Call Enhanced Analyzer
   └─ Collect results
   ↓
Generate Summary
   ├─ Count toxic/safe
   ├─ Calculate averages
   ├─ Identify top categories
   └─ Level distribution
   ↓
Log to Analytics
   ↓
Return Results + Summary
```

### Analytics Flow
```
Any Analysis
   ↓
Analytics Engine
   ↓
Log Entry
   ├─ Timestamp
   ├─ Score
   ├─ Level
   ├─ Categories
   └─ Matches
   ↓
Save to JSON
   ├─ Append to messages[]
   ├─ Update daily_stats{}
   └─ Keep last 1000
   ↓
Calculate Insights
   ├─ Trends (7-day)
   ├─ Patterns
   ├─ Peak hours
   └─ AI insights
   ↓
Display on Dashboard
```

---

## 🎯 WORKFLOW EXAMPLES

### Workflow 1: Content Moderation
```
1. User posts message
   ↓
2. POST /api/chat/moderate
   ↓
3. Analyzer checks toxicity
   ↓
4. If HIGH → Block message
   If MEDIUM → Warn user
   If LOW → Allow with log
   ↓
5. Track user behavior
   ↓
6. Update risk score
   ↓
7. Recommend actions
```

### Workflow 2: Batch Report Generation
```
1. Upload chat log CSV
   ↓
2. Batch analyze all messages
   ↓
3. View summary statistics
   ↓
4. Export as HTML report
   ↓
5. Present to stakeholders
```

### Workflow 3: Trend Analysis
```
1. Analyze messages daily
   ↓
2. Check /analytics dashboard
   ↓
3. Review 7-day trends
   ↓
4. Check AI insights
   ↓
5. Act on recommendations
```

### Workflow 4: Message Improvement
```
1. Analyze original message
   ↓
2. Get AI suggestions
   ↓
3. Use /comparison tool
   ↓
4. Compare original vs improved
   ↓
5. See improvement percentage
   ↓
6. Choose best alternative
```

---

## 🎓 LEARNING PATH

### Beginner Path
```
Day 1: Explore Home Page
├─ Analyze sample messages
├─ See category breakdown
└─ Try AI suggestions

Day 2: Use Comparison Tool
├─ Compare before/after
├─ Test examples
└─ Understand metrics

Day 3: Check Analytics
├─ View trends
├─ Read insights
└─ Understand heatmap
```

### Advanced Path
```
Week 1: API Integration
├─ Test /predict endpoint
├─ Build client app
└─ Handle responses

Week 2: Batch Processing
├─ Upload datasets
├─ Process 1000+ messages
└─ Generate reports

Week 3: Custom Development
├─ Modify templates
├─ Add features
└─ Deploy to cloud
```

---

## 🔍 TROUBLESHOOTING MAP

```
Problem: Server won't start
   ├─ Check: Port 5000 in use?
   ├─ Check: Virtual env activated?
   └─ Check: Dependencies installed?

Problem: Analytics empty
   ├─ Check: Analyzed any messages?
   ├─ Check: analytics_history.json exists?
   └─ Solution: Analyze some messages first

Problem: Charts not loading
   ├─ Check: Internet connection?
   ├─ Check: Browser console errors?
   └─ Solution: Hard refresh (Ctrl+Shift+R)

Problem: Export fails
   ├─ Check: Results array not empty?
   ├─ Check: Format parameter valid?
   └─ Solution: Check API payload
```

---

## 🚀 QUICK ACCESS LINKS

**When Server is Running:**

| Feature | Direct Link |
|---------|-------------|
| Home | [http://127.0.0.1:5000/](http://127.0.0.1:5000/) |
| Chat | [http://127.0.0.1:5000/chat-analyzer](http://127.0.0.1:5000/chat-analyzer) |
| Dashboard | [http://127.0.0.1:5000/live-dashboard](http://127.0.0.1:5000/live-dashboard) |
| Compare | [http://127.0.0.1:5000/comparison](http://127.0.0.1:5000/comparison) |
| Analytics | [http://127.0.0.1:5000/analytics](http://127.0.0.1:5000/analytics) |
| Batch | [http://127.0.0.1:5000/batch](http://127.0.0.1:5000/batch) |

---

## 📊 METRICS DASHBOARD

```
Total Features:        15+
Total Pages:           6
Total API Endpoints:   15+
Total Files:           30+
Lines of Code:         2,500+
Database Words:        2,000+
Export Formats:        3
Chart Types:           4
Auto-refresh Rate:     2-30s
Max Batch Size:        1,000+
```

---

**Use this map to navigate your enhanced toxicity detection system!** 🗺️
