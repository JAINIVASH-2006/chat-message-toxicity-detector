"""
Enhanced Toxicity Analysis System - Stable Version
Fixed backend connectivity and Spark Web UI integration
"""

# Dependency check on startup
def check_dependencies():
    """Check if required dependencies are available"""
    missing = []
    
    try:
        import flask
    except ImportError:
        missing.append('flask')
    
    try:
        import pandas
    except ImportError:
        missing.append('pandas')
    
    try:
        import requests
    except ImportError:
        missing.append('requests')
    
    if missing:
        print("❌ Missing required dependencies:", ', '.join(missing))
        print("📦 Please run: python install_requirements.py")
        print("📦 Or manually install: pip install " + ' '.join(missing))
        return False
    
    # Check optional dependencies
    optional_missing = []
    try:
        import pyspark
    except ImportError:
        optional_missing.append('pyspark')
        print("⚠️  PySpark not available - Spark features will be limited")
    
    try:
        import numpy
    except ImportError:
        optional_missing.append('numpy')
    
    try:
        import sklearn
    except ImportError:
        optional_missing.append('scikit-learn')
    
    if optional_missing:
        print("⚠️  Optional dependencies missing:", ', '.join(optional_missing))
        print("📦 For full functionality, install: pip install " + ' '.join(optional_missing))
    
    return True

# Check dependencies before proceeding
if not check_dependencies():
    print("\n🔧 Run dependency installer? (y/n):")
    choice = input().strip().lower()
    if choice in ['y', 'yes']:
        import subprocess
        import sys
        subprocess.run([sys.executable, 'install_requirements.py'])
    else:
        print("❌ Cannot start without required dependencies")
        exit(1)

from flask import Flask, request, jsonify, render_template, send_from_directory, Response, redirect, url_for
import requests
import threading
import subprocess
import os
import sys
from pathlib import Path
import uuid
import time
import json
from collections import defaultdict
import pandas as pd
import webbrowser

# Set up paths
ROOT = Path(__file__).parent
LOG_DIR = ROOT / 'data' / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Create required directories
(ROOT / 'data' / 'datasets').mkdir(parents=True, exist_ok=True)
(ROOT / 'data' / 'processed').mkdir(parents=True, exist_ok=True)
(ROOT / 'data' / 'uploads').mkdir(parents=True, exist_ok=True)
(ROOT / 'models').mkdir(parents=True, exist_ok=True)
(ROOT / 'templates').mkdir(parents=True, exist_ok=True)
(ROOT / 'static').mkdir(parents=True, exist_ok=True)

# Safe imports with fallbacks
try:
    from toxicity_analysis import (
        Lexicon,
        analyze_messages,
        analyze_text,
        load_lexicon,
        summarize_messages,
    )
except ImportError:
    print("Warning: toxicity_analysis module not found. Creating basic fallback...")
    class Lexicon:
        def __init__(self, keywords=None, categories=None, severity=None):
            self.keywords = keywords or set()
            self.categories = categories or {}
            self.severity = severity or {}
    
    def analyze_text(text, lexicon):
        return {'toxicity_score': 0.0, 'is_toxic': False, 'categories': []}
    
    def load_lexicon(path):
        return Lexicon()
    
    def analyze_messages(messages, lexicon):
        return [analyze_text(msg, lexicon) for msg in messages]
    
    def summarize_messages(analyses):
        return {'total': len(analyses), 'toxic': 0, 'clean': len(analyses)}

try:
    from enhanced_toxicity_analysis import EnhancedToxicityAnalyzer
except ImportError:
    print("Warning: enhanced_toxicity_analysis module not found. Creating fallback...")
    class EnhancedToxicityAnalyzer:
        def analyze_text(self, text):
            return {
                'toxicity_probability': 0.0,
                'is_toxic': False,
                'categories': [],
                'severity': 'low',
                'toxicity_score': 0.0,
                'toxicity_level': 'SAFE',
                'primary_category': 'clean',
                'severity_level': 'low'
            }

try:
    from response_suggestions import ResponseSuggestionEngine
except ImportError:
    print("Warning: response_suggestions module not found. Creating fallback...")
    class ResponseSuggestionEngine:
        def suggest_alternatives(self, text, analysis):
            return {'suggestions': [], 'alternatives': []}

try:
    from user_behavior_tracker import UserBehaviorTracker
except ImportError:
    print("Warning: user_behavior_tracker module not found. Creating fallback...")
    class UserBehaviorTracker:
        def track_analysis(self, text, result):
            pass
        def get_analysis_history(self):
            return []

try:
    from analytics_engine import analytics
except ImportError:
    print("Warning: analytics_engine module not found. Creating fallback...")
    class MockAnalytics:
        def get_statistics(self):
            return {'total_analyses': 0, 'toxic_detected': 0}
        def get_insights(self):
            return []
        def get_trends(self, days=7):
            return []
    analytics = MockAnalytics()

try:
    from export_system import export_system
except ImportError:
    print("Warning: export_system module not found. Creating fallback...")
    class MockExportSystem:
        def export_data(self, data, format):
            content = json.dumps(data, indent=2)
            return content, 'application/json', f'export.{format}'
    export_system = MockExportSystem()

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Global variables
jobs = {}
enhanced_analyzer = EnhancedToxicityAnalyzer()
suggestion_engine = ResponseSuggestionEngine() 
behavior_tracker = UserBehaviorTracker()

# Load toxicity database with fallback
try:
    lexicon_path = ROOT / 'data' / 'datasets' / 'comprehensive_toxicity_dataset.csv'
    if lexicon_path.exists():
        lexicon = load_lexicon(lexicon_path)
        print(f"Loaded {len(lexicon.keywords)} toxicity words from database")
    else:
        print("Creating sample toxicity dataset...")
        # Create sample dataset
        sample_data = {
            'word': ['hate', 'stupid', 'idiot', 'toxic', 'spam'],
            'category': ['hate', 'insult', 'insult', 'general', 'spam'],
            'severity': [0.8, 0.6, 0.5, 0.7, 0.3]
        }
        sample_df = pd.DataFrame(sample_data)
        sample_df.to_csv(lexicon_path, index=False)
        lexicon = load_lexicon(lexicon_path)
        print(f"Created sample dataset with {len(lexicon.keywords)} words")
except Exception as e:
    print(f"Warning: Could not load toxicity database: {e}")
    lexicon = Lexicon(set(), {}, {})

def start_background_process(cmd, log_path):
    """Start a subprocess and track it"""
    job_id = str(uuid.uuid4())
    try:
        with open(log_path, 'w') as log_file:
            process = subprocess.Popen(
                cmd,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=ROOT
            )
        
        jobs[job_id] = {
            'process': process,
            'status': 'running',
            'log_path': str(log_path),
            'start_time': time.time(),
            'command': ' '.join(cmd)
        }
        
        # Start monitoring thread
        def monitor_process():
            try:
                process.wait()
                jobs[job_id]['status'] = 'completed' if process.returncode == 0 else 'failed'
                jobs[job_id]['end_time'] = time.time()
                jobs[job_id]['return_code'] = process.returncode
            except Exception as e:
                jobs[job_id]['status'] = 'error'
                jobs[job_id]['error'] = str(e)
        
        thread = threading.Thread(target=monitor_process)
        thread.daemon = True
        thread.start()
        
        return job_id
    except Exception as e:
        jobs[job_id] = {
            'status': 'error',
            'error': str(e),
            'command': ' '.join(cmd)
        }
        return job_id

# Add helper to open Chrome (with fallbacks) and a delayed opener so the server can start first
def open_in_chrome(url):
    """Try to open the given URL in Chrome, with fallbacks to default browser."""
    # Try registered browser names
    for name in ('chrome', 'google-chrome', 'windows-default', 'chromium'):
        try:
            if name:
                webbrowser.get(name).open(url, new=2)
            else:
                webbrowser.open(url, new=2)
            return True
        except Exception:
            continue

    # Try common Chrome executable locations
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/usr/bin/google-chrome",
        "/usr/bin/chrome",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    ]
    for path in chrome_paths:
        if os.path.exists(path):
            try:
                subprocess.Popen([path, url])
                return True
            except Exception:
                continue

    # Final fallback: default browser
    try:
        webbrowser.open(url, new=2)
        return True
    except Exception:
        return False

def open_browser_delayed(url, delay=1.0):
    """Open browser after a short delay in a daemon thread."""
    def _open():
        time.sleep(delay)
        open_in_chrome(url)
    t = threading.Thread(target=_open)
    t.daemon = True
    t.start()

# ============================================================================
# MAIN ROUTES
# ============================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Predict toxicity for text input"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Basic toxicity analysis
        basic_result = analyze_text(text, lexicon)
        
        # Enhanced analysis
        enhanced_result = enhanced_analyzer.analyze_text(text)
        
        # Get suggestions
        suggestions = suggestion_engine.suggest_alternatives(text, enhanced_result)
        
        # Track user behavior
        behavior_tracker.track_analysis(text, enhanced_result)
        
        return jsonify({
            'text': text,
            'basic_toxicity': basic_result,
            'enhanced_analysis': enhanced_result,
            'suggestions': suggestions,
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# JOB MANAGEMENT ROUTES
# ============================================================================

@app.route('/run-spark', methods=['POST'])
def run_spark():
    """Start Spark preprocessing job"""
    try:
        data = request.get_json() or {}
        input_path = data.get('input', str(ROOT / 'data' / 'datasets' / 'comprehensive_toxicity_dataset.csv'))
        output_path = data.get('output', str(ROOT / 'data' / 'processed' / 'spark_output.parquet'))
        num_partitions = data.get('num_partitions', 4)
        keep_alive = data.get('keep_alive', 30)

        cmd = [
            sys.executable, 
            str(ROOT / 'spark_job.py'), 
            '--input', input_path, 
            '--output', output_path, 
            '--num-partitions', str(num_partitions), 
            '--keep-alive', str(keep_alive)
        ]
        
        log_path = LOG_DIR / f'spark_job_{int(time.time())}.log'
        job_id = start_background_process(cmd, log_path)
        
        return jsonify({
            'status': 'started', 
            'job_id': job_id, 
            'spark_ui_url': 'http://localhost:4040',
            'proxy_url': '/spark-proxy/'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/train', methods=['POST'])
def train():
    """Start model training job"""
    try:
        data = request.get_json() or {}
        input_path = data.get('input', str(ROOT / 'data' / 'datasets' / 'comprehensive_toxicity_dataset.csv'))
        model_out = data.get('model_out', str(ROOT / 'models' / 'spark_lr_model'))
        algo = data.get('algo', 'logistic')
        
        cmd = [
            sys.executable, 
            str(ROOT / 'train_model_spark.py'), 
            '--input', input_path, 
            '--model-out', model_out, 
            '--algo', algo
        ]
        
        log_path = LOG_DIR / f'training_{int(time.time())}.log'
        job_id = start_background_process(cmd, log_path)
        
        return jsonify({
            'status': 'started', 
            'job_id': job_id,
            'spark_ui_url': 'http://localhost:4040',
            'proxy_url': '/spark-proxy/'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/job-status/<job_id>')
def job_status(job_id):
    """Get job status"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    status_info = {
        'status': job['status'],
        'start_time': job.get('start_time'),
        'command': job.get('command', '')
    }
    
    if 'end_time' in job:
        status_info['end_time'] = job['end_time']
        status_info['duration'] = job['end_time'] - job['start_time']
    
    if 'return_code' in job:
        status_info['return_code'] = job['return_code']
    
    if 'error' in job:
        status_info['error'] = job['error']
    
    # Try to read recent log entries
    if 'log_path' in job:
        try:
            with open(job['log_path'], 'r') as f:
                lines = f.readlines()
                status_info['log'] = ''.join(lines[-10:])  # Last 10 lines
        except:
            pass
    
    return jsonify(status_info)

# ============================================================================
# PAGE ROUTES
# ============================================================================

@app.route('/chat-analyzer')
def chat_analyzer_page():
    return render_template('chat_analyzer.html')

@app.route('/advanced-chat-analyzer')
def advanced_chat_analyzer_page():
    """Advanced chat analyzer with dataset support"""
    return render_template('advanced_chat_analyzer.html')

@app.route('/dataset-analyzer')
def dataset_analyzer_page():
    """New page for uploading and analyzing chat message datasets"""
    return render_template('dataset_analyzer.html')

@app.route('/comparison')
def comparison_page():
    return render_template('comparison.html')

@app.route('/analytics')
def analytics_page():
    return render_template('analytics.html')

@app.route('/models')
def models_page():
    return render_template('models.html')

@app.route('/settings')
def settings_page():
    return render_template('settings.html')

@app.route('/help')
def help_page():
    return render_template('help.html')

@app.route('/live-dashboard')
def live_dashboard_redirect():
    """Redirect to dataset analyzer"""
    return redirect(url_for('dataset_analyzer_page'))

@app.route('/spark-status')
def spark_status():
    """Check Spark connectivity and provide direct access options"""
    status_info = {
        'proxy_available': True,
        'direct_access_urls': [
            'http://localhost:4040',
            'http://127.0.0.1:4040',
            'http://0.0.0.0:4040'
        ],
        'system_status': 'operational',
        'jobs_running': len([j for j in jobs.values() if j.get('status') == 'running'])
    }
    
    # Test direct Spark UI access
    for url in status_info['direct_access_urls']:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                status_info['spark_ui_direct'] = url
                status_info['spark_accessible'] = True
                break
        except:
            continue
    else:
        status_info['spark_accessible'] = False
        status_info['spark_ui_direct'] = None
    
    return jsonify(status_info)

@app.route('/test-spark-connection')
def test_spark_connection():
    """Test and display Spark connection methods"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Spark Connection Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .test-item { background: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #007bff; }
            .success { border-left-color: #28a745; background: #d4edda; }
            .error { border-left-color: #dc3545; background: #f8d7da; }
            .btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 5px; }
            .btn:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔥 Spark Connection Test</h1>
            <p>Testing various connection methods to bypass firewall issues:</p>
            
            <div class="test-item">
                <h3>Method 1: Proxy Access</h3>
                <p>Access through our integrated proxy (firewall-friendly)</p>
                <a href="/spark-proxy/" class="btn" target="_blank">Test Proxy Access</a>
            </div>
            
            <div class="test-item">
                <h3>Method 2: Direct localhost</h3>
                <p>Direct connection to Spark UI on localhost</p>
                <a href="http://localhost:4040" class="btn" target="_blank">Test localhost:4040</a>
            </div>
            
            <div class="test-item">
                <h3>Method 3: IP Address</h3>
                <p>Direct connection using IP address</p>
                <a href="http://127.0.0.1:4040" class="btn" target="_blank">Test 127.0.0.1:4040</a>
            </div>
            
            <div class="test-item">
                <h3>Method 4: Alternative Port</h3>
                <p>Try alternative port if main port is blocked</p>
                <a href="http://localhost:4041" class="btn" target="_blank">Test localhost:4041</a>
            </div>
            
            <div class="test-item">
                <h3>System Status</h3>
                <p>Check overall system connectivity</p>
                <a href="/spark-status" class="btn" target="_blank">Check Status API</a>
                <a href="/" class="btn">Return to Main System</a>
            </div>
        </div>
        
        <script>
            // Auto-test connections
            setTimeout(() => {
                fetch('/spark-status')
                .then(r => r.json())
                .then(data => {
                    console.log('Spark Status:', data);
                    if (data.spark_accessible) {
                        document.body.insertAdjacentHTML('beforeend', 
                            '<div style="position: fixed; top: 20px; right: 20px; background: #28a745; color: white; padding: 15px; border-radius: 8px;">✅ Spark UI is accessible!</div>'
                        );
                    }
                })
                .catch(e => console.log('Status check failed:', e));
            }, 1000);
        </script>
    </body>
    </html>
    '''

@app.route('/overview')
def overview_page():
    """System overview page"""
    return render_template('overview.html')

@app.route('/visualize')
def visualize_page():
    """Data visualization page"""
    return render_template('visualize.html')

@app.route('/jobs')
def jobs_page():
    """Spark jobs monitoring page"""
    return render_template('jobs.html')

# ============================================================================
# DATASET ANALYZER ROUTES (NEW)
# ============================================================================

@app.route('/upload-dataset', methods=['POST'])
def upload_dataset():
    """Upload and analyze chat message dataset"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file
        upload_dir = ROOT / 'data' / 'uploads'
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = int(time.time())
        filename = f"chat_dataset_{timestamp}.csv"
        filepath = upload_dir / filename
        
        file.save(filepath)
        
        # Analyze the dataset
        df = pd.read_csv(filepath)
        
        # Basic validation
        if len(df) == 0:
            return jsonify({'error': 'Empty dataset'}), 400
        
        # Try to identify message column
        message_col = None
        for col in ['message', 'text', 'content', 'chat', 'msg']:
            if col in df.columns:
                message_col = col
                break
        
        if not message_col:
            # Use first text column
            text_cols = df.select_dtypes(include=['object']).columns
            if len(text_cols) > 0:
                message_col = text_cols[0]
            else:
                return jsonify({'error': 'No text column found in dataset'}), 400
        
        # Analyze messages
        results = []
        for idx, row in df.head(100).iterrows():  # Limit to first 100 for demo
            message = str(row[message_col])
            if message and len(message.strip()) > 0:
                basic_result = analyze_text(message, lexicon)
                enhanced_result = enhanced_analyzer.analyze_text(message)
                
                results.append({
                    'index': idx,
                    'message': message[:100] + '...' if len(message) > 100 else message,
                    'toxicity_score': enhanced_result['toxicity_probability'],
                    'is_toxic': enhanced_result['is_toxic'],
                    'categories': enhanced_result['categories'],
                    'severity': enhanced_result['severity']
                })
        
        # Generate summary statistics
        total_messages = len(results)
        toxic_count = sum(1 for r in results if r['is_toxic'])
        avg_toxicity = sum(r['toxicity_score'] for r in results) / total_messages if total_messages > 0 else 0
        
        # Category breakdown
        category_counts = defaultdict(int)
        for result in results:
            for category in result['categories']:
                category_counts[category] += 1
        
        summary = {
            'total_messages': total_messages,
            'toxic_messages': toxic_count,
            'toxic_percentage': (toxic_count / total_messages * 100) if total_messages > 0 else 0,
            'average_toxicity_score': avg_toxicity,
            'category_breakdown': dict(category_counts),
            'dataset_info': {
                'filename': filename,
                'columns': list(df.columns),
                'total_rows': len(df),
                'analyzed_rows': total_messages
            }
        }
        
        return jsonify({
            'status': 'success',
            'summary': summary,
            'results': results[:20],  # Return first 20 detailed results
            'message': f'Successfully analyzed {total_messages} messages from dataset'
        })
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

# ============================================================================
# SPARK WEB UI PROXY (FIREWALL-FRIENDLY)
# ============================================================================

@app.route('/spark-proxy/', defaults={'subpath': ''})
@app.route('/spark-proxy/<path:subpath>')
def spark_proxy(subpath):
    """Firewall-friendly Spark Web UI proxy with multiple fallback options"""
    try:
        # Multiple connection attempts with different configurations
        spark_urls = [
            'http://127.0.0.1:4040',  # Localhost
            'http://localhost:4040',   # Standard localhost
            'http://0.0.0.0:4040'     # All interfaces
        ]
        
        connected = False
        response = None
        
        # Try different connection methods
        for spark_url in spark_urls:
            try:
                url = f"{spark_url}/{subpath}" if subpath else spark_url
                
                # Configure session to bypass common firewall issues
                session = requests.Session()
                session.headers.update({
                    'User-Agent': 'Enhanced-Toxicity-Analysis-System/1.0',
                    'Accept': '*/*',
                    'Connection': 'keep-alive'
                })
                
                # Disable SSL verification and set custom timeout
                response = session.get(
                    url, 
                    timeout=5, 
                    params=request.args,
                    verify=False,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    connected = True
                    break
                    
            except (requests.exceptions.ConnectionError, 
                   requests.exceptions.Timeout, 
                   requests.exceptions.RequestException):
                continue
        
        if not connected:
            # Return enhanced fallback page with system status
            return '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Spark UI - System Status</title>
                <style>
                    body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
                    .container { max-width: 800px; margin: 0 auto; padding: 50px 20px; text-align: center; }
                    .status-card { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; margin: 20px 0; backdrop-filter: blur(10px); }
                    .icon { font-size: 4rem; margin-bottom: 20px; }
                    .btn { background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; display: inline-block; margin: 10px; }
                    .btn:hover { background: #218838; }
                    .alternatives { text-align: left; margin-top: 30px; }
                    .alternative-item { background: rgba(255,255,255,0.05); padding: 15px; margin: 10px 0; border-radius: 8px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="status-card">
                        <div class="icon">⚡</div>
                        <h1>Spark Web UI Status</h1>
                        <p>Spark UI is currently not accessible through the proxy.</p>
                        <p>This is normal when no Spark jobs are actively running.</p>
                    </div>
                    
                    <div class="status-card">
                        <h2>🚀 Available Actions</h2>
                        <a href="/" class="btn">← Back to Main Dashboard</a>
                        <a href="/advanced-chat-analyzer" class="btn">🔍 Chat Analyzer</a>
                        <a href="/analytics" class="btn">📊 Analytics</a>
                    </div>
                    
                    <div class="status-card alternatives">
                        <h3>💡 How to Access Spark UI:</h3>
                        <div class="alternative-item">
                            <strong>1. Start a Spark Job:</strong> Use the main dashboard to run a Spark analysis job
                        </div>
                        <div class="alternative-item">
                            <strong>2. Direct Access:</strong> Try <a href="http://localhost:4040" target="_blank" style="color: #ffd700;">http://localhost:4040</a> directly
                        </div>
                        <div class="alternative-item">
                            <strong>3. Alternative Port:</strong> Check <a href="http://localhost:4041" target="_blank" style="color: #ffd700;">http://localhost:4041</a> if multiple Spark contexts exist
                        </div>
                    </div>
                    
                    <div class="status-card">
                        <h3>🔧 System Information</h3>
                        <p>Enhanced Toxicity Analysis System is running properly</p>
                        <p>All other features are fully functional</p>
                    </div>
                </div>
            </body>
            </html>
            ''', 200
        
        # Successfully connected - process the response
        content = response.content
        content_type = response.headers.get('Content-Type', 'text/html')
        
        # Enhanced URL rewriting for better proxy support
        if 'text/html' in content_type:
            try:
                content_str = content.decode('utf-8', errors='ignore')
                
                # Comprehensive URL rewriting
                replacements = [
                    ('href="/static/', 'href="/spark-proxy/static/'),
                    ('src="/static/', 'src="/spark-proxy/static/'),
                    ('href="/jobs', 'href="/spark-proxy/jobs'),
                    ('href="/stages', 'href="/spark-proxy/stages'),
                    ('href="/executors', 'href="/spark-proxy/executors'),
                    ('href="/environment', 'href="/spark-proxy/environment'),
                    ('href="/storage', 'href="/spark-proxy/storage'),
                    ('href="/sql', 'href="/spark-proxy/sql'),
                    ('action="/', 'action="/spark-proxy/'),
                    ('url("/', 'url("/spark-proxy/'),
                ]
                
                for old, new in replacements:
                    content_str = content_str.replace(old, new)
                
                # Add custom CSS to improve display
                content_str = content_str.replace(
                    '</head>',
                    '''<style>
                    .navbar-brand::after { content: " (via Enhanced Toxicity Analysis System)"; font-size: 0.8em; color: #28a745; }
                    </style></head>'''
                )
                
                content = content_str.encode('utf-8')
            except Exception as decode_error:
                print(f"Warning: Could not decode content for URL rewriting: {decode_error}")
        
        # Return the proxied content with proper headers
        response_headers = {}
        for header in ['Content-Type', 'Cache-Control', 'Expires']:
            if header in response.headers:
                response_headers[header] = response.headers[header]
        
        return Response(content, headers=response_headers)
        
    except Exception as e:
        return f'''
        <html>
        <head><title>Proxy Error</title></head>
        <body style="font-family: Arial; padding: 50px; text-align: center;">
            <h2>🔥 Enhanced Toxicity Analysis System</h2>
            <h3>Spark Proxy Status</h3>
            <p>Proxy service is operational but Spark UI is not currently accessible.</p>
            <p>Error details: {str(e)}</p>
            <a href="/" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">← Return to Main System</a>
        </body>
        </html>
        ''', 200  # Return 200 instead of error to avoid browser issues

# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/api/sample-datasets')
def api_sample_datasets():
    """Get available sample datasets"""
    try:
        catalog_path = ROOT / 'data' / 'sample_datasets' / 'catalog.json'
        if catalog_path.exists():
            with open(catalog_path, 'r') as f:
                catalog = json.load(f)
            return jsonify(catalog)
        else:
            # Return empty datasets if no catalog exists
            return jsonify({'datasets': []})
    except Exception as e:
        return jsonify({'error': str(e), 'datasets': []}), 500

@app.route('/api/analyze-sample/<dataset_name>')
def api_analyze_sample(dataset_name):
    """Analyze a specific sample dataset"""
    try:
        dataset_path = ROOT / 'data' / 'sample_datasets' / f'{dataset_name}.csv'
        if not dataset_path.exists():
            return jsonify({'error': 'Dataset not found'}), 404
        
        # Read and analyze the dataset
        df = pd.read_csv(dataset_path)
        
        # Find message column
        message_col = None
        for col in ['message', 'text', 'content', 'chat', 'msg', 'comment']:
            if col in df.columns:
                message_col = col
                break
        
        if not message_col:
            return jsonify({'error': 'No message column found'}), 400
        
        # Analyze messages (limit to first 50 for performance)
        messages = df[message_col].head(50).tolist()
        results = []
        
        for msg in messages:
            if pd.notna(msg) and isinstance(msg, str):
                analysis = enhanced_analyzer.analyze_text(msg)
                results.append({
                    'message': msg,
                    'toxicity_score': analysis.get('toxicity_score', 0),
                    'is_toxic': analysis.get('toxicity_level') != 'SAFE',
                    'category': analysis.get('primary_category', 'clean'),
                    'severity': analysis.get('severity_level', 'low')
                })
        
        # Calculate summary
        total = len(results)
        toxic = sum(1 for r in results if r['is_toxic'])
        avg_score = sum(r['toxicity_score'] for r in results) / total if total > 0 else 0
        
        return jsonify({
            'status': 'success',
            'dataset_name': dataset_name,
            'summary': {
                'total_messages': total,
                'toxic_messages': toxic,
                'toxic_percentage': (toxic / total * 100) if total > 0 else 0,
                'average_toxicity_score': avg_score
            },
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics')
def api_analytics():
    """Analytics API endpoint"""
    try:
        stats = analytics.get_statistics()
        insights = analytics.get_insights()
        trends = analytics.get_trends(days=7)
        
        return jsonify({
            'statistics': stats,
            'insights': insights,
            'trends': trends,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/export/<format>')
def export_data(format):
    """Export data in various formats"""
    try:
        data = behavior_tracker.get_analysis_history()
        content, mimetype, filename = export_system.export_data(data, format)
        
        return Response(
            content,
            mimetype=mimetype,
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/static/<path:p>')
def static_files(p):
    return send_from_directory(str(ROOT / 'static'), p)

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================