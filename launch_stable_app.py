#!/usr/bin/env python3
"""
Stable Flask App Launcher with Error Recovery
"""

import os
import sys
import time
from pathlib import Path

# Set working directory
ROOT = Path(__file__).parent
os.chdir(ROOT)

# Add to Python path
sys.path.insert(0, str(ROOT))

def launch_app():
    """Launch Flask app with error handling"""
    try:
        print("🔥 Starting Enhanced Toxicity Analysis System...")
        print("=" * 60)
        
        # Import and configure app
        from app_stable import app
        
        print("✅ Flask app imported successfully")
        print("🌐 Server starting on http://127.0.0.1:5000")
        print("📊 All features: Toxicity Analysis, Spark Jobs, Dataset Analyzer")
        print("⚡ Spark UI Proxy: http://127.0.0.1:5000/spark-proxy/")
        print("")
        
        # Start server
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            use_reloader=False,
            threaded=True
        )
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Try: pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ Server Error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = launch_app()
    if not success:
        print("\n🛑 Server failed to start")
        sys.exit(1)
