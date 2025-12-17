# 🚀 CMD Setup Guide - Enhanced Toxicity Analysis System

## Quick Start (3 Simple Steps!)

### Step 1: Run Setup
```cmd
SETUP.bat
```
This will:
- ✅ Check Python installation
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Verify all modules load correctly

### Step 2: Start Application
```cmd
START_APP_CMD.bat
```
Or use quick start:
```cmd
QUICK_START.bat
```

### Step 3: Open Browser
Navigate to: **http://127.0.0.1:5000**

---

## 📋 Detailed Instructions

### Prerequisites
- **Python 3.8 or higher** installed
- **Internet connection** (for downloading packages)
- **Windows CMD** or **PowerShell**

### Installation Steps

#### Option 1: Automatic Setup (Recommended)
1. Open CMD in the project folder
2. Run: `SETUP.bat`
3. Wait for installation to complete
4. Run: `START_APP_CMD.bat`

#### Option 2: Manual Setup
```cmd
REM Navigate to project folder
cd "d:\spark main"

REM Create virtual environment
python -m venv .venv

REM Activate virtual environment
.venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install requirements
pip install -r requirements.txt

REM Verify installation
python -c "from app import app; print('Setup complete!')"

REM Start server
python app.py
```

---

## 🎯 Available Scripts

### 1. SETUP.bat
**Purpose:** First-time setup and dependency installation
```cmd
SETUP.bat
```
**What it does:**
- Checks Python installation
- Creates virtual environment (.venv)
- Installs all requirements
- Verifies module loading

### 2. START_APP_CMD.bat
**Purpose:** Start the Flask server (with logs visible)
```cmd
START_APP_CMD.bat
```
**What it does:**
- Activates virtual environment
- Checks port availability
- Starts Flask server
- Shows server logs in console

### 3. QUICK_START.bat
**Purpose:** Quick start with automatic Chrome launch
```cmd
QUICK_START.bat
```
**What it does:**
- Runs setup if needed
- Starts server in background
- Opens Chrome automatically
- Press any key to stop

### 4. TEST_COMPONENTS.bat
**Purpose:** Test all installed components
```cmd
TEST_COMPONENTS.bat
```
**What it does:**
- Tests Flask
- Tests pandas
- Tests PySpark
- Tests all custom modules
- Shows ✓ or ✗ for each component

### 5. START_IN_CHROME.bat
**Purpose:** PowerShell version with advanced features
```cmd
START_IN_CHROME.bat
```

---

## 📦 Requirements Explained

### Core Framework
```
flask==2.3.2          → Web framework for the application
werkzeug==2.3.6       → WSGI utilities for Flask
```

### Data Processing
```
pandas==2.2.3         → Data manipulation and analysis
numpy>=1.21.0         → Numerical computing
pyarrow>=10.0.0       → Fast data serialization
```

### Machine Learning & NLP
```
pyspark==4.0.1        → Distributed data processing
datasets==2.16.1      → Dataset loading and processing
transformers==4.35.0  → NLP models (future use)
```

### HTTP & API
```
requests==2.31.0      → HTTP library
urllib3==2.0.4        → HTTP client
```

### Utilities
```
python-dotenv==1.0.0  → Environment variables
tqdm==4.66.1          → Progress bars
findspark==2.0.1      → Spark initialization
```

---

## 🔧 Troubleshooting

### Problem 1: "Python is not recognized"
**Solution:**
1. Install Python from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Restart CMD and try again

### Problem 2: "Failed to create virtual environment"
**Solution:**
```cmd
python -m pip install --upgrade pip
python -m pip install virtualenv
python -m virtualenv .venv
```

### Problem 3: "pip install fails"
**Solution:**
```cmd
REM Upgrade pip first
python -m pip install --upgrade pip

REM Install with verbose output
pip install -r requirements.txt -v

REM If specific package fails, install manually
pip install flask==2.3.2
pip install pandas==2.2.3
```

### Problem 4: "Port 5000 already in use"
**Solution:**
```cmd
REM Find process using port 5000
netstat -ano | findstr :5000

REM Kill the process (replace PID with actual number)
taskkill /F /PID <PID>

REM Or use QUICK_START.bat which does this automatically
```

### Problem 5: "Module not found"
**Solution:**
```cmd
REM Activate virtual environment first
.venv\Scripts\activate.bat

REM Reinstall requirements
pip install -r requirements.txt --force-reinstall

REM Verify installation
python -c "from app import app; print('OK')"
```

### Problem 6: "ImportError: enhanced_toxicity_analysis"
**Solution:**
```cmd
REM Make sure you're in the project directory
cd "d:\spark main"

REM Check if file exists
dir enhanced_toxicity_analysis.py

REM If it exists, check for syntax errors
python -m py_compile enhanced_toxicity_analysis.py
```

---

## 🧪 Testing the Setup

### Test 1: Check Python
```cmd
python --version
```
Expected: `Python 3.8.x` or higher

### Test 2: Check Virtual Environment
```cmd
.venv\Scripts\activate.bat
python -c "import sys; print(sys.prefix)"
```
Expected: Path should contain `.venv`

### Test 3: Check Modules
```cmd
python -c "import flask; print(flask.__version__)"
python -c "import pandas; print(pandas.__version__)"
python -c "import pyspark; print(pyspark.__version__)"
```

### Test 4: Check Custom Modules
```cmd
python -c "from enhanced_toxicity_analysis import EnhancedToxicityAnalyzer; print('OK')"
python -c "from analytics_engine import analytics; print('OK')"
python -c "from export_system import export_system; print('OK')"
```

### Test 5: Check Server
```cmd
REM In one CMD window
python app.py

REM In another CMD window
curl http://127.0.0.1:5000
```
Or visit in browser: http://127.0.0.1:5000

---

## 📊 Component Test Results

Run `TEST_COMPONENTS.bat` to see:
```
[1/8] Testing Flask...
✓ Flask OK

[2/8] Testing pandas...
✓ pandas OK

[3/8] Testing requests...
✓ requests OK

[4/8] Testing PySpark...
✓ PySpark OK

[5/8] Testing toxicity_analysis...
✓ toxicity_analysis OK

[6/8] Testing enhanced_toxicity_analysis...
✓ EnhancedToxicityAnalyzer OK

[7/8] Testing analytics_engine...
✓ analytics_engine OK

[8/8] Testing export_system...
✓ export_system OK
```

---

## 🎯 Complete Workflow

### First Time Setup
```cmd
REM 1. Clone or extract project
cd "d:\spark main"

REM 2. Run setup
SETUP.bat

REM 3. Wait for completion (2-5 minutes)

REM 4. Start application
START_APP_CMD.bat

REM 5. Open browser to http://127.0.0.1:5000
```

### Daily Usage
```cmd
REM Quick start (recommended)
QUICK_START.bat

REM Or manual start
START_APP_CMD.bat
```

### Stopping the Server
- Press `Ctrl+C` in the terminal
- Or close the CMD window
- Or use Task Manager to kill python.exe

---

## 🌐 Accessing the Application

### Main URLs
- **Home:** http://127.0.0.1:5000/
- **Chat Analyzer:** http://127.0.0.1:5000/chat-analyzer
- **Live Dashboard:** http://127.0.0.1:5000/live-dashboard
- **Analytics:** http://127.0.0.1:5000/analytics
- **Batch Processing:** http://127.0.0.1:5000/batch
- **Health Check:** http://127.0.0.1:5000/health

### API Endpoints
- **Predict:** POST http://127.0.0.1:5000/predict
- **Batch Analyze:** POST http://127.0.0.1:5000/api/batch-analyze
- **Export:** POST http://127.0.0.1:5000/api/export

---

## 📁 Project Structure
```
d:\spark main\
├── app.py                          ← Main Flask application
├── enhanced_toxicity_analysis.py   ← Enhanced analyzer
├── analytics_engine.py             ← Analytics system
├── export_system.py                ← Export functionality
├── requirements.txt                ← Python dependencies
├── SETUP.bat                       ← Setup script
├── START_APP_CMD.bat               ← Start script
├── QUICK_START.bat                 ← Quick launcher
├── TEST_COMPONENTS.bat             ← Component tester
├── .venv\                          ← Virtual environment (created by setup)
├── data\
│   ├── datasets\
│   │   └── comprehensive_toxicity_dataset.csv
│   └── logs\
├── models\
├── static\
│   ├── style.css
│   └── app.js
└── templates\
    ├── index.html
    ├── chat_analyzer.html
    ├── live_dashboard.html
    ├── analytics.html
    └── batch.html
```

---

## 💡 Tips & Best Practices

### 1. Always Use Virtual Environment
```cmd
REM Activate before any Python command
.venv\Scripts\activate.bat
```

### 2. Keep Requirements Updated
```cmd
REM After installing new packages
pip freeze > requirements.txt
```

### 3. Check Logs
```cmd
REM Server logs appear in the console
REM Application logs in data/logs/
```

### 4. Monitor Performance
```cmd
REM Visit health check endpoint
curl http://127.0.0.1:5000/health
```

### 5. Backup Configuration
```cmd
REM Copy your requirements before updates
copy requirements.txt requirements_backup.txt
```

---

## 🚀 Advanced Usage

### Run in Production Mode
```cmd
REM Install production server
pip install waitress

REM Start with waitress
waitress-serve --host=127.0.0.1 --port=5000 app:app
```

### Run with Gunicorn (if on Linux/WSL)
```cmd
gunicorn -w 4 -b 127.0.0.1:5000 app:app
```

### Enable Debug Mode
Edit `app.py`, ensure last line is:
```python
app.run(debug=True)
```

### Disable Debug Mode
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

---

## ✅ Verification Checklist

Before using the application, verify:

- [ ] Python 3.8+ installed
- [ ] Virtual environment created (.venv folder exists)
- [ ] All requirements installed (no errors in SETUP.bat)
- [ ] All components test OK (TEST_COMPONENTS.bat passes)
- [ ] Server starts without errors
- [ ] Port 5000 is accessible
- [ ] Browser can load http://127.0.0.1:5000
- [ ] Home page displays correctly
- [ ] Toxicity analysis works (test with sample text)
- [ ] Navigation to all pages works

---

## 🎉 Success Indicators

You'll know everything is working when:

1. **SETUP.bat** completes with:
   ```
   ✓ All modules loaded successfully
   Setup Complete!
   ```

2. **START_APP_CMD.bat** shows:
   ```
   Loaded 696 toxicity words from database
   * Running on http://127.0.0.1:5000
   ```

3. **Browser** displays the home page at http://127.0.0.1:5000

4. **Health check** returns:
   ```json
   {
     "status": "healthy",
     "components": {
       "flask": "running",
       "enhanced_analyzer": "loaded",
       "lexicon": "696 words loaded"
     }
   }
   ```

---

## 📞 Need Help?

If you encounter issues:

1. Run `TEST_COMPONENTS.bat` to identify failed components
2. Check the error messages in the console
3. Review the troubleshooting section above
4. Ensure you have internet connection during setup
5. Try reinstalling in a fresh virtual environment

---

*Last Updated: November 5, 2025*  
*System: Enhanced Toxicity Analysis*  
*Platform: Windows CMD/PowerShell*
