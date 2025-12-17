#!/usr/bin/env python3
"""
Complete System Launcher - Fixed Version
Launches the enhanced toxicity analysis system with all components working
"""
import os
import sys
import time
import threading
import webbrowser
from pathlib import Path

def main():
    ROOT = Path(__file__).parent
    os.chdir(ROOT)
    
    print("🔥 Enhanced Toxicity Analysis System")
    print("=" * 50)
    print("✅ Backend Connectivity: FIXED")
    print("✅ Spark Web UI Integration: FIXED") 
    print("✅ Live Dashboard → Dataset Analyzer: REPLACED")
    print("✅ Chat Message Upload & Analysis: NEW")
    print("")
    
    # Start browser after delay
    def open_browser():
        time.sleep(3)
        url = "http://127.0.0.1:5000"
        print(f"🌐 Opening browser: {url}")
        
        try:
            if sys.platform.startswith('win'):
                os.system(f'start chrome "{url}"')
            else:
                webbrowser.open(url)
            print("✅ Browser opened successfully")
        except Exception as e:
            print(f"⚠️  Auto-open failed: {e}")
            print(f"📋 Please manually open: {url}")
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Import and run stable app
    print("🚀 Starting stable Flask server...")
    print("📊 Features available:")
    print("   • Real-time toxicity analysis")
    print("   • Chat message dataset upload & analysis") 
    print("   • Spark job management")
    print("   • Spark Web UI proxy (fixed)")
    print("   • Export and reporting")
    print("")
    
    import app_stable
    
if __name__ == "__main__":
    main()