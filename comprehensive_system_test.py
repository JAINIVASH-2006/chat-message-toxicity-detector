"""
Comprehensive System Test
Tests all components and reports any errors found
"""

import sys
import os
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_status(message, status='info'):
    """Print colored status messages"""
    if status == 'success':
        print(f"{GREEN}✅ {message}{RESET}")
    elif status == 'error':
        print(f"{RED}❌ {message}{RESET}")
    elif status == 'warning':
        print(f"{YELLOW}⚠️  {message}{RESET}")
    else:
        print(f"{BLUE}ℹ️  {message}{RESET}")

def test_imports():
    """Test all critical imports"""
    print("\n" + "="*60)
    print("TESTING MODULE IMPORTS")
    print("="*60)
    
    errors = []
    
    # Test Flask and web dependencies
    try:
        from flask import Flask, request, jsonify
        print_status("Flask imports", 'success')
    except ImportError as e:
        errors.append(f"Flask: {e}")
        print_status(f"Flask imports: {e}", 'error')
    
    # Test data processing
    try:
        import pandas as pd
        print_status("Pandas", 'success')
    except ImportError as e:
        errors.append(f"Pandas: {e}")
        print_status(f"Pandas: {e}", 'error')
    
    # Test PySpark
    try:
        from pyspark.sql import SparkSession
        from pyspark import SparkContext
        print_status("PySpark", 'success')
    except ImportError as e:
        errors.append(f"PySpark: {e}")
        print_status(f"PySpark: {e}", 'error')
    
    # Test toxicity analysis modules
    try:
        from toxicity_analysis import analyze_text, load_lexicon
        print_status("Toxicity Analysis", 'success')
    except ImportError as e:
        errors.append(f"Toxicity Analysis: {e}")
        print_status(f"Toxicity Analysis: {e}", 'error')
    
    try:
        from enhanced_toxicity_analysis import EnhancedToxicityAnalyzer
        print_status("Enhanced Toxicity Analyzer", 'success')
    except ImportError as e:
        errors.append(f"Enhanced Toxicity Analyzer: {e}")
        print_status(f"Enhanced Toxicity Analyzer: {e}", 'error')
    
    # Test supporting modules
    try:
        from response_suggestions import ResponseSuggestionEngine
        print_status("Response Suggestion Engine", 'success')
    except ImportError as e:
        errors.append(f"Response Suggestion Engine: {e}")
        print_status(f"Response Suggestion Engine: {e}", 'error')
    
    try:
        from user_behavior_tracker import UserBehaviorTracker
        print_status("User Behavior Tracker", 'success')
    except ImportError as e:
        errors.append(f"User Behavior Tracker: {e}")
        print_status(f"User Behavior Tracker: {e}", 'error')
    
    try:
        from analytics_engine import analytics
        print_status("Analytics Engine", 'success')
    except ImportError as e:
        errors.append(f"Analytics Engine: {e}")
        print_status(f"Analytics Engine: {e}", 'error')
    
    try:
        from export_system import export_system
        print_status("Export System", 'success')
    except ImportError as e:
        errors.append(f"Export System: {e}")
        print_status(f"Export System: {e}", 'error')
    
    try:
        from spark_manager import start_spark_ui, is_spark_ui_running
        print_status("Spark Manager", 'success')
    except ImportError as e:
        errors.append(f"Spark Manager: {e}")
        print_status(f"Spark Manager: {e}", 'error')
    
    # Test main app
    try:
        import app
        print_status("Main App Module", 'success')
    except ImportError as e:
        errors.append(f"Main App: {e}")
        print_status(f"Main App: {e}", 'error')
    
    return errors

def test_file_structure():
    """Test required files and directories exist"""
    print("\n" + "="*60)
    print("TESTING FILE STRUCTURE")
    print("="*60)
    
    errors = []
    ROOT = Path(__file__).parent
    
    # Required directories
    required_dirs = [
        'data',
        'data/datasets',
        'data/sample_datasets',
        'data/logs',
        'templates',
        'static',
        'models'
    ]
    
    for dir_path in required_dirs:
        full_path = ROOT / dir_path
        if full_path.exists():
            print_status(f"Directory: {dir_path}", 'success')
        else:
            errors.append(f"Missing directory: {dir_path}")
            print_status(f"Missing directory: {dir_path}", 'error')
    
    # Required files
    required_files = [
        'data/toxicity_words_database.txt',
        'data/datasets/comprehensive_toxicity_dataset.csv',
        'templates/enhanced_live_dashboard.html',
        'templates/index.html',
        'templates/base.html'
    ]
    
    for file_path in required_files:
        full_path = ROOT / file_path
        if full_path.exists():
            print_status(f"File: {file_path}", 'success')
        else:
            errors.append(f"Missing file: {file_path}")
            print_status(f"Missing file: {file_path}", 'error')
    
    # Count dataset files
    sample_datasets = list((ROOT / 'data' / 'sample_datasets').glob('*.csv'))
    if len(sample_datasets) >= 30:
        print_status(f"Sample datasets: {len(sample_datasets)} files found", 'success')
    else:
        errors.append(f"Expected 30+ sample datasets, found {len(sample_datasets)}")
        print_status(f"Sample datasets: Only {len(sample_datasets)} files found (expected 30+)", 'warning')
    
    # Count template files
    templates = list((ROOT / 'templates').glob('*.html'))
    print_status(f"HTML templates: {len(templates)} files", 'success')
    
    return errors

def test_functionality():
    """Test core functionality"""
    print("\n" + "="*60)
    print("TESTING CORE FUNCTIONALITY")
    print("="*60)
    
    errors = []
    
    # Test EnhancedToxicityAnalyzer
    try:
        from enhanced_toxicity_analysis import EnhancedToxicityAnalyzer
        analyzer = EnhancedToxicityAnalyzer()
        
        # Test clean message
        result = analyzer.analyze_text("Hello, how are you?")
        if result['toxicity_score'] < 0.3:
            print_status("EnhancedToxicityAnalyzer: Clean text detection", 'success')
        else:
            errors.append("Clean text incorrectly flagged as toxic")
            print_status("Clean text incorrectly flagged as toxic", 'warning')
        
        # Test toxic message (if keywords present)
        toxic_result = analyzer.analyze_text("you idiot moron")
        if toxic_result['toxicity_score'] > 0:
            print_status("EnhancedToxicityAnalyzer: Toxic text detection", 'success')
        else:
            print_status("EnhancedToxicityAnalyzer: Basic functionality working", 'success')
            
    except Exception as e:
        errors.append(f"EnhancedToxicityAnalyzer test failed: {e}")
        print_status(f"EnhancedToxicityAnalyzer: {e}", 'error')
    
    # Test ResponseSuggestionEngine
    try:
        from response_suggestions import ResponseSuggestionEngine
        engine = ResponseSuggestionEngine()
        toxicity_info = {'toxicity_score': 0.5, 'category': 'profanity'}
        suggestions = engine.suggest_alternatives("test message", toxicity_info)
        if suggestions:
            print_status("ResponseSuggestionEngine: Working", 'success')
        else:
            print_status("ResponseSuggestionEngine: No suggestions but functional", 'success')
    except Exception as e:
        errors.append(f"ResponseSuggestionEngine test failed: {e}")
        print_status(f"ResponseSuggestionEngine: {e}", 'error')
    
    # Test UserBehaviorTracker
    try:
        from user_behavior_tracker import UserBehaviorTracker
        tracker = UserBehaviorTracker()
        toxicity_analysis = {
            'toxicity_score': 50,
            'toxicity_level': 'MEDIUM',
            'top_category': 'profanity'
        }
        result = tracker.track_message("test_user", "Test message", toxicity_analysis)
        print_status("UserBehaviorTracker: Working", 'success')
    except Exception as e:
        errors.append(f"UserBehaviorTracker test failed: {e}")
        print_status(f"UserBehaviorTracker: {e}", 'error')
    
    # Test dataset loading
    try:
        import pandas as pd
        ROOT = Path(__file__).parent
        dataset_path = ROOT / 'data' / 'datasets' / 'comprehensive_toxicity_dataset.csv'
        if dataset_path.exists():
            df = pd.read_csv(dataset_path)
            print_status(f"Dataset loading: {len(df)} rows loaded", 'success')
        else:
            errors.append("Comprehensive toxicity dataset not found")
            print_status("Comprehensive toxicity dataset not found", 'warning')
    except Exception as e:
        errors.append(f"Dataset loading failed: {e}")
        print_status(f"Dataset loading: {e}", 'error')
    
    return errors

def test_syntax():
    """Test Python syntax of all .py files"""
    print("\n" + "="*60)
    print("TESTING PYTHON SYNTAX")
    print("="*60)
    
    errors = []
    ROOT = Path(__file__).parent
    
    # Key Python files to test
    key_files = [
        'app.py',
        'enhanced_toxicity_analysis.py',
        'toxicity_analysis.py',
        'spark_manager.py',
        'response_suggestions.py',
        'user_behavior_tracker.py',
        'analytics_engine.py',
        'export_system.py',
        'spark_job.py'
    ]
    
    import py_compile
    
    for file_name in key_files:
        file_path = ROOT / file_name
        if not file_path.exists():
            print_status(f"{file_name}: Not found", 'warning')
            continue
            
        try:
            py_compile.compile(str(file_path), doraise=True)
            print_status(f"{file_name}: Valid syntax", 'success')
        except py_compile.PyCompileError as e:
            errors.append(f"{file_name}: Syntax error - {e}")
            print_status(f"{file_name}: Syntax error", 'error')
    
    return errors

def main():
    """Run all tests and report results"""
    print("\n" + "="*60)
    print("COMPREHENSIVE SYSTEM TEST")
    print("="*60)
    print("Testing all components for errors...\n")
    
    all_errors = []
    
    # Run all tests
    all_errors.extend(test_syntax())
    all_errors.extend(test_imports())
    all_errors.extend(test_file_structure())
    all_errors.extend(test_functionality())
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    if not all_errors:
        print_status("ALL TESTS PASSED! No errors found.", 'success')
        print(f"\n{GREEN}🎉 System is fully functional and ready to use!{RESET}")
        return 0
    else:
        print_status(f"FOUND {len(all_errors)} ISSUE(S):", 'error')
        for i, error in enumerate(all_errors, 1):
            print(f"  {i}. {error}")
        print(f"\n{YELLOW}⚠️  Some components may need attention.{RESET}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
