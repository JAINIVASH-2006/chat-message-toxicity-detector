# Toxicity Analysis Project - Current Status

## ✅ What's Working

### 1. Flask Web Dashboard (Currently Running)
- **URL**: http://127.0.0.1:5000
- **Status**: ✅ ACTIVE
- **Features**:
  - Heuristic toxicity analysis (keyword-based)
  - Real-time message scoring
  - Dataset analysis endpoint
  - Chat interface for message analysis
  - Model training and prediction interface

### 2. Toxicity Analysis Module
- **File**: `toxicity_analysis.py`
- **Status**: ✅ FIXED (corruption removed)
- **Functionality**:
  - Lexicon-based scoring using keywords from dataset
  - Risk level classification (LOW/MEDIUM/HIGH)
  - Batch message analysis
  - Summary statistics generation

### 3. Dataset Analysis Tool
- **File**: `analyze_dataset.py`
- **Status**: ✅ READY
- **Usage**: `python analyze_dataset.py data/datasets/comprehensive_toxicity_dataset.csv`
- **Features**:
  - CLI batch processing
  - Column auto-detection
  - Summary statistics

## ⚠️ Known Issues

### Java 25 Incompatibility
**Problem**: Spark 3.4.1 + Hadoop 3.4.1 are incompatible with Java 25

**Error**: `java.lang.UnsupportedOperationException: getSubject is not supported`

**Why**: Java 25 deprecated `Subject.getSubject()` method that Hadoop still uses

**Impact**: 
- ❌ Spark Web UI not accessible (http://localhost:4040)
- ❌ Cannot run `spark_job.py` preprocessing
- ❌ Cannot run `train_model_spark.py` training

## 🔧 Solutions

### Option 1: Install Java 17 (RECOMMENDED)
**Steps**:
1. Download Java 17 LTS from: https://adoptium.net/temurin/releases/?version=17
2. Install to `C:\Program Files\Java\jdk-17`
3. Run the provided batch file: `run_spark_with_java17.bat`
   - Or manually set: `$env:JAVA_HOME="C:\Program Files\Java\jdk-17"`
4. Then run: `python spark_job.py --input data/datasets/comprehensive_toxicity_dataset.csv --output data/datasets/comprehensive_toxicity_dataset.parquet --keep-alive 600`
5. Access Spark UI at: http://localhost:4040

**Benefits**:
- ✅ Full Spark functionality
- ✅ Spark Web UI accessible
- ✅ Compatible with all Spark/Hadoop features
- ✅ LTS (Long Term Support) version

### Option 2: Use Flask Dashboard Only (CURRENT)
**What You Have Now**:
- ✅ Heuristic toxicity analysis (fast, no Spark needed)
- ✅ Web interface for message analysis
- ✅ Dataset audit and statistics
- ✅ Real-time predictions

**Limitations**:
- ❌ No distributed processing
- ❌ No Spark ML models
- ❌ No Spark Web UI monitoring

### Option 3: Upgrade to Spark 4.0+ (FUTURE)
- Spark 4.0+ supports Java 25
- Currently in preview/not stable
- Would require code updates

## 📁 Project Structure

```
d:\spark main\
├── app.py                          # ✅ Flask web server (RUNNING)
├── toxicity_analysis.py            # ✅ Heuristic scoring module (FIXED)
├── analyze_dataset.py              # ✅ CLI analysis tool
├── spark_job.py                    # ⚠️ Preprocessing (needs Java 17)
├── train_model_spark.py            # ⚠️ Training pipeline (needs Java 17)
├── run_spark_with_java17.bat       # 🆕 Helper script for Java 17
├── start_server.bat                # Flask launcher
├── requirements.txt                # Dependencies
├── data/
│   └── datasets/
│       └── comprehensive_toxicity_dataset.csv  # Main dataset
├── models/
│   └── spark_lr_model/             # Previously trained model
├── templates/                      # HTML templates
│   ├── index.html                  # Main dashboard
│   ├── chat.html                   # Chat interface
│   ├── overview.html               # Dataset overview
│   └── ...
└── static/                         # CSS/JS assets
    ├── style.css
    └── app.js
```

## 🎯 Next Steps

### Immediate Actions:
1. **Install Java 17** (if you want Spark UI)
   - Download: https://adoptium.net/temurin/releases/?version=17
   - Install and update `run_spark_with_java17.bat` with correct path
   
2. **Use Flask Dashboard** (already working)
   - Open http://127.0.0.1:5000 in Chrome
   - Test message analysis
   - View dataset statistics

### Once Java 17 is Installed:
1. Run: `run_spark_with_java17.bat`
2. Open Chrome with two tabs:
   - Tab 1: http://127.0.0.1:5000 (Flask Dashboard)
   - Tab 2: http://localhost:4040 (Spark Web UI)
3. Use Flask to trigger Spark jobs
4. Monitor execution in Spark UI

## 🔍 How to Analyze Messages

### Method 1: Web Interface (Current)
1. Go to http://127.0.0.1:5000
2. Enter message in "Quick Toxicity Check" section
3. Click "Analyze Message"
4. View toxicity score and risk level

### Method 2: CLI Tool
```powershell
python analyze_dataset.py data/datasets/comprehensive_toxicity_dataset.csv
```

### Method 3: API Endpoint
```bash
curl -X POST http://127.0.0.1:5000/predict -H "Content-Type: application/json" -d '{"message":"your text here"}'
```

## 📊 Dataset Analysis

Your comprehensive toxicity dataset contains:
- Multiple text samples
- Various toxicity categories
- Keyword patterns for heuristic scoring

**To analyze**:
1. Use Flask dashboard: http://127.0.0.1:5000/overview
2. Or run CLI: `python analyze_dataset.py data/datasets/comprehensive_toxicity_dataset.csv`

## 🐛 Debugging Tips

### If Flask won't start:
```powershell
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill process if needed
taskkill /PID <pid> /F

# Restart Flask
& "D:/spark main/.venv/Scripts/python.exe" app.py
```

### If Spark fails with Java errors:
1. Check Java version: `java -version`
2. Should show Java 17, not Java 25
3. Set JAVA_HOME: `$env:JAVA_HOME="C:\Program Files\Java\jdk-17"`
4. Verify: `$env:JAVA_HOME`

### If dataset not found:
- Check path: `data/datasets/comprehensive_toxicity_dataset.csv`
- Verify with: `Test-Path "data/datasets/comprehensive_toxicity_dataset.csv"`

## 📝 Technical Notes

### Heuristic Scoring Algorithm
The `toxicity_analysis.py` module uses:
1. **Keyword extraction** from dataset categories
2. **Weighted scoring** based on keyword matches
3. **Risk classification** (LOW < 0.3, MEDIUM 0.3-0.6, HIGH > 0.6)
4. **Category detection** based on matched patterns

### Flask Endpoints
- `GET /` - Main dashboard
- `POST /predict` - Single message analysis
- `GET /api/messages/dataset-analysis` - Full dataset audit
- `GET /chat` - Chat interface
- `POST /download` - Dataset download
- `POST /run-spark` - Trigger Spark job
- `POST /train` - Train ML model

### Spark Configuration
When Java 17 is available:
- Local mode: `local[*]` (uses all CPU cores)
- Event logging: `spark-events/` directory
- Web UI: http://localhost:4040 (automatic)
- History server: Available after jobs complete

## 🎓 Resources

### Documentation
- Apache Spark: https://spark.apache.org/docs/latest/
- Flask: https://flask.palletsprojects.com/
- PySpark: https://spark.apache.org/docs/latest/api/python/

### Downloads
- Java 17 (Temurin): https://adoptium.net/temurin/releases/?version=17
- Python 3.11: https://www.python.org/downloads/

### Troubleshooting
- Spark + Java 25 issue: https://issues.apache.org/jira/browse/SPARK-45429
- Hadoop winutils: https://github.com/cdarlint/winutils

---

**Last Updated**: Now  
**Status**: Flask dashboard operational, Spark pending Java 17 installation
