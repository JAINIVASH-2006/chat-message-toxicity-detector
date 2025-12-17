#!/usr/bin/env python3
"""
Chrome Launcher with Comprehensive Firewall Bypass
"""

import subprocess
import time
import os
import platform
from pathlib import Path

def find_chrome():
    """Find Chrome executable on system"""
    if platform.system() == "Windows":
        chrome_paths = [
            "C:/Program Files/Google/Chrome/Application/chrome.exe",
            "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
            os.path.expanduser("~/AppData/Local/Google/Chrome/Application/chrome.exe")
        ]
    else:
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/chrome",
            "/usr/bin/chromium-browser"
        ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            return path
    
    return "chrome"  # Hope it's in PATH

def launch_system_in_chrome():
    """Launch the complete system in Chrome with firewall bypass"""
    chrome_path = find_chrome()
    
    # Comprehensive firewall bypass flags
    chrome_flags = [
        "--disable-web-security",
        "--allow-running-insecure-content", 
        "--disable-features=VizDisplayCompositor",
        "--proxy-bypass-list=localhost,127.0.0.1,0.0.0.0",
        "--disable-site-isolation-trials",
        "--disable-features=BlockInsecurePrivateNetworkRequests",
        "--allow-insecure-localhost",
        "--ignore-certificate-errors",
        "--ignore-ssl-errors",
        "--ignore-certificate-errors-spki-list",
        "--user-data-dir=" + str(Path.home() / "chrome-toxicity-analysis")
    ]
    
    # URLs to open
    urls = [
        "http://127.0.0.1:5000",                           # Main Dashboard
        "http://127.0.0.1:5000/advanced-chat-analyzer",    # Advanced Analyzer
        "http://127.0.0.1:5000/analytics",                 # Analytics
        "http://127.0.0.1:5000/test-spark-connection",     # Connection Test
        "http://127.0.0.1:5000/spark-proxy/"               # Spark Proxy
    ]
    
    print("🚀 Launching Enhanced Toxicity Analysis System in Chrome...")
    print("🛡️ Using comprehensive firewall bypass flags")
    
    try:
        # Launch first URL with flags
        cmd = [chrome_path] + chrome_flags + [urls[0]]
        subprocess.Popen(cmd)
        
        # Wait and launch additional tabs
        time.sleep(3)
        for url in urls[1:]:
            cmd = [chrome_path] + chrome_flags + [url]
            subprocess.Popen(cmd)
            time.sleep(1)
            
        print("✅ All system components launched in Chrome!")
        print("🌐 Main Dashboard: http://127.0.0.1:5000")
        
    except Exception as e:
        print(f"❌ Chrome launch failed: {e}")
        print("💡 Try opening http://127.0.0.1:5000 manually")

if __name__ == '__main__':
    launch_system_in_chrome()
