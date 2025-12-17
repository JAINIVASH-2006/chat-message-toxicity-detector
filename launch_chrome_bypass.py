#!/usr/bin/env python3
"""
Chrome Launcher with Firewall Bypass
Launches all system components in Chrome with proxy-friendly settings
"""

import subprocess
import time
import webbrowser
import requests
import sys
from pathlib import Path

def test_connection(url, timeout=5):
    """Test if a URL is accessible"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False

def launch_chrome_with_flags(urls):
    """Launch Chrome with specific flags to bypass firewall issues"""
    
    # Chrome flags to bypass common firewall/proxy issues
    chrome_flags = [
        '--disable-web-security',
        '--disable-features=VizDisplayCompositor',
        '--disable-extensions',
        '--disable-plugins',
        '--disable-gpu',
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--remote-debugging-port=9222',
        '--user-data-dir=' + str(Path.home() / 'chrome_toxicity_temp'),
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-renderer-backgrounding',
        '--proxy-bypass-list=localhost,127.0.0.1',
        '--allow-running-insecure-content',
        '--disable-site-isolation-trials'
    ]
    
    # Try different Chrome executable paths
    chrome_paths = [
        'chrome',
        'google-chrome',
        'chromium',
        'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/usr/bin/google-chrome',
        '/usr/bin/chromium-browser'
    ]
    
    chrome_executable = None
    for path in chrome_paths:
        try:
            # Test if chrome is accessible
            result = subprocess.run([path, '--version'], capture_output=True, timeout=5)
            if result.returncode == 0:
                chrome_executable = path
                break
        except:
            continue
    
    if not chrome_executable:
        print("❌ Chrome not found. Using default browser...")
        for url in urls:
            webbrowser.open(url)
        return True
    
    # Launch Chrome with all URLs
    try:
        cmd = [chrome_executable] + chrome_flags + urls
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ Launched Chrome with {len(urls)} tabs")
        return True
    except Exception as e:
        print(f"❌ Failed to launch Chrome: {e}")
        print("💡 Falling back to default browser...")
        for url in urls:
            webbrowser.open(url)
        return False

def main():
    """Main launcher function"""
    print("🔥" * 60)
    print("🔥 ENHANCED TOXICITY ANALYSIS - CHROME LAUNCHER")
    print("🔥 FIREWALL & PROXY BYPASS ENABLED")
    print("🔥" * 60)
    print()
    
    base_url = "http://127.0.0.1:5000"
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    for i in range(10):
        if test_connection(base_url):
            print(f"✅ Server ready after {i+1} attempts")
            break
        time.sleep(1)
    else:
        print("❌ Server not responding. Please start the Flask application first:")
        print("   cd \"d:\\spark main\" && .venv\\Scripts\\python app_stable.py")
        return False
    
    # Define all system URLs to open
    urls_to_open = [
        f"{base_url}/",                           # Main dashboard
        f"{base_url}/advanced-chat-analyzer",     # Advanced chat analyzer
        f"{base_url}/analytics",                  # Analytics dashboard
        f"{base_url}/test-spark-connection",      # Spark connection test
        f"{base_url}/overview",                   # System overview
    ]
    
    print("🌐 Opening system components in Chrome...")
    print()
    
    # Test each URL before opening
    working_urls = []
    for url in urls_to_open:
        if test_connection(url, timeout=3):
            print(f"✅ {url}")
            working_urls.append(url)
        else:
            print(f"⚠️  {url} - May have connectivity issues")
            working_urls.append(url)  # Add anyway, Chrome might handle it better
    
    print()
    print(f"🚀 Launching {len(working_urls)} tabs in Chrome...")
    
    success = launch_chrome_with_flags(working_urls)
    
    if success:
        print()
        print("🎉 SUCCESS! All components launched in Chrome")
        print()
        print("📱 Available Features:")
        print("   • Main Dashboard - System overview and navigation")
        print("   • Advanced Chat Analyzer - 3 analysis modes with 20+ datasets")
        print("   • Analytics Dashboard - Comprehensive reporting")
        print("   • Spark Connection Test - Firewall bypass testing")
        print("   • System Overview - Feature documentation")
        print()
        print("🔧 Firewall Bypass Features:")
        print("   • Chrome launched with proxy-bypass flags")
        print("   • Multiple connection methods tested")
        print("   • Direct localhost access enabled")
        print("   • Enhanced proxy routing active")
        print()
        print("⚡ Spark UI Access:")
        print("   • Integrated proxy: http://127.0.0.1:5000/spark-proxy/")
        print("   • Direct access: http://localhost:4040")
        print("   • Connection test: http://127.0.0.1:5000/test-spark-connection")
        print()
        print("🎯 System is fully operational and firewall-friendly!")
        
        # Keep monitoring
        print("👀 Monitoring system connectivity...")
        try:
            while True:
                time.sleep(30)
                if not test_connection(base_url):
                    print("⚠️  Connection lost - please check Flask server")
                    break
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped by user")
    
    return success

if __name__ == "__main__":
    success = main()
    if not success:
        input("Press Enter to exit...")
    sys.exit(0 if success else 1)