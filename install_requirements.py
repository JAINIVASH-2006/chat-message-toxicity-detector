"""
Automated Requirements Installer for Enhanced Toxicity Analysis System
Handles dependency installation with fallbacks and error handling
"""
import subprocess
import sys
import os
import time
from pathlib import Path

ROOT = Path(__file__).parent

def check_python_version():
    """Check if Python version is compatible"""
    major, minor = sys.version_info[:2]
    print(f"🐍 Python version: {major}.{minor}")
    
    if major < 3 or (major == 3 and minor < 8):
        print("❌ Python 3.8+ is required")
        print("Please upgrade Python and try again")
        return False
    
    print("✅ Python version is compatible")
    return True

def upgrade_pip():
    """Upgrade pip to latest version"""
    print("🔧 Upgrading pip...")
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ pip upgraded successfully")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Warning: Could not upgrade pip, continuing...")
        return False

def install_package(package, retries=3):
    """Install a single package with retries"""
    for attempt in range(retries):
        try:
            print(f"📦 Installing {package}... (attempt {attempt + 1}/{retries})")
            
            # Try different installation methods
            install_commands = [
                [sys.executable, '-m', 'pip', 'install', package],
                [sys.executable, '-m', 'pip', 'install', package, '--user'],
                [sys.executable, '-m', 'pip', 'install', package, '--no-cache-dir'],
                [sys.executable, '-m', 'pip', 'install', package, '--force-reinstall']
            ]
            
            for cmd in install_commands:
                try:
                    result = subprocess.run(
                        cmd, 
                        capture_output=True, 
                        text=True, 
                        timeout=300  # 5 minute timeout
                    )
                    
                    if result.returncode == 0:
                        print(f"✅ Successfully installed {package}")
                        return True
                    
                except subprocess.TimeoutExpired:
                    print(f"⏰ Timeout installing {package}, trying alternative method...")
                    continue
                except Exception as e:
                    print(f"⚠️  Error with command {' '.join(cmd)}: {e}")
                    continue
            
            # If all methods failed, wait and retry
            if attempt < retries - 1:
                print(f"⏳ Waiting 5 seconds before retry...")
                time.sleep(5)
                
        except Exception as e:
            print(f"❌ Error installing {package}: {e}")
            if attempt == retries - 1:
                return False
    
    return False

def install_requirements():
    """Install all requirements from requirements.txt"""
    requirements_file = ROOT / 'requirements.txt'
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found!")
        return False
    
    print(f"📋 Reading requirements from {requirements_file}")
    
    with open(requirements_file, 'r') as f:
        packages = []
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                packages.append(line)
    
    print(f"📦 Found {len(packages)} packages to install")
    
    # Core packages (install first)
    core_packages = ['pip', 'setuptools', 'wheel']
    optional_packages = []
    required_packages = []
    
    # Categorize packages
    for package in packages:
        package_name = package.split('>=')[0].split('==')[0].split('<')[0]
        if package_name in ['pyspark', 'nltk', 'textblob']:
            optional_packages.append(package)
        else:
            required_packages.append(package)
    
    # Install core packages first
    print("\n🔧 Installing core packages...")
    for package in core_packages:
        install_package(package)
    
    # Install required packages
    print(f"\n📦 Installing {len(required_packages)} required packages...")
    failed_required = []
    for package in required_packages:
        if not install_package(package):
            failed_required.append(package)
    
    # Install optional packages (don't fail if these don't work)
    print(f"\n🎯 Installing {len(optional_packages)} optional packages...")
    failed_optional = []
    for package in optional_packages:
        if not install_package(package):
            failed_optional.append(package)
    
    # Report results
    print("\n" + "="*60)
    print("📊 INSTALLATION SUMMARY")
    print("="*60)
    
    total_packages = len(required_packages) + len(optional_packages)
    successful = total_packages - len(failed_required) - len(failed_optional)
    
    print(f"✅ Successfully installed: {successful}/{total_packages} packages")
    
    if failed_required:
        print(f"❌ Failed required packages: {', '.join(failed_required)}")
    
    if failed_optional:
        print(f"⚠️  Failed optional packages: {', '.join(failed_optional)}")
    
    # Check if system can still run
    critical_failed = [pkg for pkg in failed_required if any(critical in pkg.lower() 
                      for critical in ['flask', 'pandas', 'requests'])]
    
    if critical_failed:
        print(f"\n❌ Critical packages failed: {', '.join(critical_failed)}")
        print("The system may not work properly. Please install these manually:")
        for pkg in critical_failed:
            print(f"   pip install {pkg}")
        return False
    
    print("\n✅ Installation completed successfully!")
    print("🚀 The system should now be ready to run")
    return True

def verify_installation():
    """Verify that key packages can be imported"""
    print("\n🔍 Verifying installation...")
    
    test_imports = [
        ('flask', 'Flask web framework'),
        ('pandas', 'Data analysis library'),
        ('requests', 'HTTP library'),
    ]
    
    optional_imports = [
        ('pyspark', 'Apache Spark'),
        ('numpy', 'Numerical computing'),
        ('sklearn', 'Machine learning'),
    ]
    
    # Test required imports
    failed_imports = []
    for module, description in test_imports:
        try:
            __import__(module)
            print(f"✅ {description}")
        except ImportError:
            print(f"❌ {description}")
            failed_imports.append(module)
    
    # Test optional imports
    for module, description in optional_imports:
        try:
            __import__(module)
            print(f"✅ {description} (optional)")
        except ImportError:
            print(f"⚠️  {description} (optional - not available)")
    
    if failed_imports:
        print(f"\n❌ Critical imports failed: {', '.join(failed_imports)}")
        return False
    
    print("\n✅ All critical packages verified successfully!")
    return True

def main():
    """Main installation function"""
    print("🔥 Enhanced Toxicity Analysis System - Dependency Installer")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Upgrade pip
    upgrade_pip()
    
    # Install packages
    if not install_requirements():
        print("\n❌ Installation failed!")
        return False
    
    # Verify installation
    if not verify_installation():
        print("\n⚠️  Some packages may not work properly")
        return False
    
    print("\n" + "="*60)
    print("🎉 SUCCESS! All dependencies installed")
    print("🚀 You can now run: python app_stable.py")
    print("="*60)
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n💡 If installation failed, try these manual commands:")
            print("   python -m pip install --upgrade pip")
            print("   python -m pip install flask pandas requests")
            print("   python -m pip install pyspark")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
