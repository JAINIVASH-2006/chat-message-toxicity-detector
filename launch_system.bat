@echo off
title Enhanced Toxicity Analysis System - Complete Setup

echo.
echo 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥
echo 🔥 ENHANCED TOXICITY ANALYSIS SYSTEM - COMPLETE LAUNCHER 🔥
echo 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥
echo.

cd /d "%~dp0"

echo 🚀 Starting system initialization...
echo.

echo 📦 Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment activated

echo.
echo 🧪 Testing system components...
python -c "
import sys
print('🔍 Component Check:')
try:
    from toxicity_analysis import load_lexicon
    print('  ✅ Toxicity analysis')
except Exception as e:
    print(f'  ❌ Toxicity analysis: {e}')

try:
    from enhanced_toxicity_analysis import EnhancedToxicityAnalyzer
    print('  ✅ Enhanced analyzer')
except Exception as e:
    print(f'  ❌ Enhanced analyzer: {e}')

try:
    from analytics_engine import AnalyticsEngine
    print('  ✅ Analytics engine')
except Exception as e:
    print(f'  ❌ Analytics engine: {e}')

try:
    import pandas as pd
    print('  ✅ Pandas library')
except Exception as e:
    print(f'  ❌ Pandas: {e}')

print('✅ Component check complete!')
"

echo.
echo 🌐 Starting Enhanced Toxicity Analysis System...
echo.
echo 📱 Application URLs:
echo    Main Interface: http://127.0.0.1:5000
echo    Advanced Chat Analyzer: http://127.0.0.1:5000/advanced-chat-analyzer
echo    Analytics Dashboard: http://127.0.0.1:5000/analytics
echo    Spark Web UI: http://127.0.0.1:5000/spark-proxy/
echo.
echo 🎯 Features Available:
echo    • Single message toxicity analysis
echo    • Dataset upload and batch processing  
echo    • 20 sample datasets with 31,950+ messages
echo    • Visual analytics and export capabilities
echo    • Spark distributed processing
echo.
echo Press Ctrl+C to stop the server when done
echo ============================================================
echo.

REM Start Flask application
python app_stable.py

echo.
echo 👋 Application stopped
pause