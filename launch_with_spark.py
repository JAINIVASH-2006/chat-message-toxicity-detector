"""
Enhanced Launcher with Proper Spark Web UI Integration
Ensures all dependencies are loaded and Spark is properly initialized
"""
import os
import sys
import time
import subprocess
from pathlib import Path

# Set up environment
ROOT = Path(__file__).parent
os.chdir(ROOT)

# Set Java environment for Spark
JAVA_HOME = os.environ.get('JAVA_HOME', r'C:\Program Files\Eclipse Adoptium\jdk-17.0.16.8-hotspot')
if os.path.exists(JAVA_HOME):
    os.environ['JAVA_HOME'] = JAVA_HOME
    os.environ['PATH'] = os.path.join(JAVA_HOME, 'bin') + os.pathsep + os.environ['PATH']
    print(f"✅ Java Home: {JAVA_HOME}")
else:
    print(f"⚠️  Warning: Java not found at {JAVA_HOME}")

# Set Spark home if available
SPARK_HOME = os.environ.get('SPARK_HOME', '')
if SPARK_HOME and os.path.exists(SPARK_HOME):
    os.environ['SPARK_HOME'] = SPARK_HOME
    print(f"✅ Spark Home: {SPARK_HOME}")

def check_dependencies():
    """Check and install required dependencies"""
    print("\n🔍 Checking dependencies...")
    
    required = ['flask', 'pandas', 'requests', 'pyspark', 'findspark']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
            print(f"  ✅ {pkg}")
        except ImportError:
            print(f"  ❌ {pkg} - MISSING")
            missing.append(pkg)
    
    if missing:
        print(f"\n📦 Installing missing packages: {', '.join(missing)}")
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing, check=True)
        print("✅ Dependencies installed!")
    else:
        print("✅ All dependencies present!")
    
    return True

def test_spark_imports():
    """Test if Spark can be imported and configured"""
    print("\n🔥 Testing Spark configuration...")
    
    try:
        import findspark
        findspark.init()
        print("  ✅ findspark initialized")
    except Exception as e:
        print(f"  ⚠️  findspark warning: {e}")
    
    try:
        from pyspark.sql import SparkSession
        print("  ✅ PySpark imports successful")
        
        # Try to create a test session
        print("  🔧 Creating test Spark session...")
        test_spark = SparkSession.builder \
            .master("local[1]") \
            .appName("TestConnection") \
            .config("spark.ui.enabled", "false") \
            .getOrCreate()
        
        # Simple test
        test_data = test_spark.createDataFrame([(1, "test")], ["id", "value"])
        count = test_data.count()
        
        test_spark.stop()
        print(f"  ✅ Spark test successful (processed {count} rows)")
        return True
        
    except Exception as e:
        print(f"  ❌ Spark test failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def start_server():
    """Start the Flask server with Spark Web UI"""
    print("\n" + "="*60)
    print("🚀 Starting Enhanced Toxicity Analysis System")
    print("="*60 + "\n")
    
    # Check port availability
    try:
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        if ':5000' in result.stdout and 'LISTENING' in result.stdout:
            print("⚠️  Port 5000 is in use. Attempting to free it...")
            # Extract PIDs and kill them
            for line in result.stdout.split('\n'):
                if ':5000' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        try:
                            subprocess.run(['taskkill', '/F', '/PID', pid], 
                                         capture_output=True, check=False)
                            print(f"  ✅ Freed port 5000 (PID: {pid})")
                        except:
                            pass
            time.sleep(2)
    except Exception as e:
        print(f"  ⚠️  Could not check port status: {e}")
    
    # Launch the main app
    print("\n🌟 Launching Flask application with Spark Web UI...")
    print("\n📍 Server will be available at:")
    print("   • Main App:        http://127.0.0.1:5000")
    print("   • Spark UI Proxy:  http://127.0.0.1:5000/spark-proxy/")
    print("   • Direct Spark UI: http://localhost:4040")
    print("\n💡 Press Ctrl+C to stop the server\n")
    print("="*60 + "\n")
    
    # Run the app
    try:
        subprocess.run([sys.executable, str(ROOT / 'app.py')], check=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")

def main():
    """Main launcher"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║  Enhanced Toxicity Analysis System - Smart Launcher  ║")
    print("╚" + "="*58 + "╝\n")
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed!")
        input("\nPress Enter to exit...")
        return 1
    
    # Step 2: Test Spark
    if not test_spark_imports():
        print("\n⚠️  Spark test failed, but continuing anyway...")
        print("   (Spark features may be limited)")
        time.sleep(2)
    
    # Step 3: Start server
    start_server()
    
    return 0

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
