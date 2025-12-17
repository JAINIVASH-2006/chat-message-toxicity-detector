"""
app.py

A small Flask app that exposes:
- GET / -> simple status page
- POST /run-spark -> trigger the PySpark preprocessing job (subprocess)
- POST /predict -> placeholder endpoint for model predictions (returns dummy results)

The Spark job runs in-process (by importing spark_job) so the Spark UI will show jobs at http://localhost:4040

Usage:
python app.py
"""
from flask import Flask, request, jsonify, render_template, send_from_directory, Response, redirect, url_for
import requests
import threading
import subprocess
import os
import sys
import json
from pathlib import Path
import uuid
import time
import re
from collections import Counter, defaultdict

import pandas as pd

from toxicity_analysis import (
  Lexicon,
  analyze_messages,
  analyze_text,
  load_lexicon,
  summarize_messages,
)

# Import enhanced toxicity analyzer
from enhanced_toxicity_analysis import EnhancedToxicityAnalyzer
from response_suggestions import ResponseSuggestionEngine
from user_behavior_tracker import UserBehaviorTracker

# NEW: Import analytics and export systems
from analytics_engine import analytics
from export_system import export_system

# Import Spark manager for persistent Web UI
from spark_manager import start_spark_ui, stop_spark_ui, is_spark_ui_running, spark_manager

app = Flask(__name__, static_folder='static', template_folder='templates')
ROOT = Path(__file__).parent
LOG_DIR = ROOT / 'data' / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Simple in-memory job tracking
jobs = {}
# Lazy-loaded Spark and model for prediction
SPARK = None
SPARK_MODEL = None
SPARK_MODEL_PATH = ROOT / 'models' / 'spark_lr_model'
ACTIVE_MODEL = None

# Heuristic toxicity lexicon derived from comprehensive dataset
LEXICON: Lexicon = Lexicon(set(), {}, {})

# Enhanced toxicity analyzer with 2000+ words
ENHANCED_ANALYZER = None
SUGGESTION_ENGINE = None
BEHAVIOR_TRACKER = None


def load_toxic_lexicon():
  """Populate the global lexicon structure from disk."""
  global LEXICON
  dataset_path = ROOT / 'data' / 'datasets' / 'comprehensive_toxicity_dataset.csv'
  LEXICON = load_lexicon(dataset_path)


def get_risk_level(score: float) -> str:
  if score < 0.3:
    return 'LOW'
  if score < 0.6:
    return 'MEDIUM'
  return 'HIGH'


def heuristic_analyze_text(text: str) -> dict:
  """Analyze text using dataset-derived keywords to approximate toxicity."""
  report = analyze_text(text, LEXICON)
  return report


# initialize lexicon once when module loads
load_toxic_lexicon()


def start_background_process(cmd: list, log_path: Path):
  """Start a subprocess and write stdout/stderr to log_path. Returns job_id."""
  job_id = str(uuid.uuid4())
  log_file = open(log_path, 'ab')
  # Start process
  proc = subprocess.Popen(cmd, stdout=log_file, stderr=subprocess.STDOUT, cwd=str(ROOT))
  jobs[job_id] = {'pid': proc.pid, 'proc': proc, 'log': str(log_path), 'start': time.time(), 'status': 'running'}

  # monitor thread to update status when finished
  def monitor():
    proc.wait()
    jobs[job_id]['status'] = 'finished' if proc.returncode == 0 else f'failed:{proc.returncode}'
    log_file.close()

  threading.Thread(target=monitor, daemon=True).start()
  return job_id


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/run-spark', methods=['POST'])
def run_spark():
  """Start the PySpark preprocessing job in background. Accepts JSON: input, output, num_partitions, keep_alive."""
  data = request.get_json() or {}
  input_path = data.get('input', str(ROOT / 'data' / 'datasets' / 'comprehensive_toxicity_dataset.csv'))
  output_path = data.get('output', str(ROOT / 'data' / 'processed' / 'spark_output.parquet'))
  num_partitions = data.get('num_partitions', 4)
  keep_alive = data.get('keep_alive', 30)  # Default 30 seconds to keep Spark UI accessible
  use_persistent_session = data.get('use_persistent_session', False)  # Use shared Spark session

  # Ensure Spark UI is running before starting jobs
  if not is_spark_ui_running() and not use_persistent_session:
    try:
      print("[*] Starting Spark UI for job monitoring...")
      start_spark_ui()
    except Exception as e:
      print(f"[!] Failed to start Spark UI: {e}")

  cmd = [sys.executable, str(ROOT / 'spark_job.py'), '--input', input_path, '--output', output_path, '--num-partitions', str(num_partitions), '--keep-alive', str(keep_alive)]
  log_path = LOG_DIR / f'spark_job_{int(time.time())}.log'
  job_id = start_background_process(cmd, log_path)
  
  spark_ui_status = "running" if is_spark_ui_running() else "starting"
  
  return jsonify({
    'status': 'started', 
    'job_id': job_id, 
    'spark_ui_url': 'http://localhost:4040',
    'spark_ui_proxy': '/spark-proxy/',
    'spark_ui_status': spark_ui_status,
    'message': f'Spark job {job_id} started. Monitor at Spark UI.'
  })


@app.route('/download-dataset', methods=['POST'])
def download_dataset():
  """Start the dataset downloader script in background. Accepts JSON: dataset, split, out, format, max_examples."""
  data = request.get_json() or {}
  dataset = data.get('dataset', 'jigsaw_toxicity_pred')
  split = data.get('split', 'train')
  out = data.get('out', str(ROOT / 'data' / 'raw' / f'{dataset}_{split}.csv'))
  fmt = data.get('format', 'csv')
  max_examples = data.get('max_examples')

  cmd = [sys.executable, str(ROOT / 'data_download.py'), '--dataset', dataset, '--split', split, '--out', out, '--format', fmt]
  if max_examples:
    cmd += ['--max-examples', str(max_examples)]
  log_path = LOG_DIR / f'download_{dataset}_{int(time.time())}.log'
  job_id = start_background_process(cmd, log_path)
  return jsonify({'status': 'started', 'job_id': job_id})


@app.route('/train', methods=['POST'])
def train():
  """Start training (train_model_spark.py) as a background job. Accepts JSON: input, model_out, algo, max_rows."""
  data = request.get_json() or {}
  input_path = data.get('input', str(ROOT / 'data' / 'datasets' / 'comprehensive_toxicity_dataset.csv'))
  model_out = data.get('model_out', str(ROOT / 'models' / 'spark_lr_model'))
  algo = data.get('algo', 'logistic')
  max_rows = data.get('max_rows')

  # Ensure Spark UI is running before starting training
  if not is_spark_ui_running():
    try:
      print("[*] Starting Spark UI for training monitoring...")
      start_spark_ui()
    except Exception as e:
      print(f"[!] Failed to start Spark UI: {e}")

  cmd = [sys.executable, str(ROOT / 'train_model_spark.py'), '--input', input_path, '--model-out', model_out, '--algo', algo]
  if max_rows:
    cmd += ['--max-rows', str(max_rows)]
  log_path = LOG_DIR / f'train_{int(time.time())}.log'
  job_id = start_background_process(cmd, log_path)
  
  spark_ui_status = "running" if is_spark_ui_running() else "starting"
  
  return jsonify({
    'status': 'started', 
    'job_id': job_id,
    'spark_ui_url': 'http://localhost:4040',
    'spark_ui_proxy': '/spark-proxy/',
    'spark_ui_status': spark_ui_status,
    'message': f'Training job {job_id} started. Monitor at Spark UI.'
  })


@app.route('/job-status/<job_id>', methods=['GET'])
def job_status(job_id):
  j = jobs.get(job_id)
  if not j:
    return jsonify({'error': 'not found'}), 404
  return jsonify({'pid': j['pid'], 'status': j['status'], 'log': j['log'], 'start': j['start']})


def tail_lines(path: Path, lines: int = 200):
  try:
    with open(path, 'rb') as f:
      f.seek(0, os.SEEK_END)
      end = f.tell()
      size = 1024
      data = b''
      while end > 0 and data.count(b'\n') <= lines:
        start = max(0, end - size)
        f.seek(start)
        data = f.read(end - start) + data
        end = start
        size *= 2
      return data.decode(errors='replace').splitlines()[-lines:]
  except FileNotFoundError:
    return []


@app.route('/job-log/<job_id>', methods=['GET'])
def job_log(job_id):
  j = jobs.get(job_id)
  if not j:
    return jsonify({'error': 'not found'}), 404
  log_path = Path(j['log'])
  lines = tail_lines(log_path, 400)
  return jsonify({'lines': lines})


@app.route('/models')
def models_page():
  return render_template('models.html')


@app.route('/visualize')
def visualize_page():
  return render_template('visualize.html')


@app.route('/jobs')
def jobs_page():
  return render_template('jobs.html')


@app.route('/settings')
def settings_page():
  return render_template('settings.html')


@app.route('/help')
def help_page():
  return render_template('help.html')


@app.route('/spark-monitor')
def spark_monitor():
  """Spark Web UI monitoring page integrated into the application"""
  return render_template('spark_monitor.html')


@app.route('/overview')
def overview_page():
    return render_template('overview.html')


@app.route('/chat')
def chat_page():
    return render_template('chat.html')

@app.route('/chat-analyzer')
def chat_analyzer_page():
    return render_template('chat_analyzer.html')

@app.route('/live-dashboard')
def live_dashboard_page():
    """Enhanced live dashboard page with multi-visualization analysis"""
    return render_template('enhanced_live_dashboard.html')

@app.route('/dataset-analyzer')
def dataset_analyzer_page():
    """Dataset analyzer page"""
    return render_template('dataset_analyzer.html')

@app.route('/comparison')
def comparison_page():
    return render_template('comparison.html')

@app.route('/analytics')
def analytics_page():
    return render_template('analytics.html')

@app.route('/batch')
def batch_page():
    return render_template('batch.html')

@app.route('/health')
def health_check():
    """System health check endpoint"""
    global ENHANCED_ANALYZER, SUGGESTION_ENGINE, BEHAVIOR_TRACKER
    
    health_status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'components': {
            'flask': 'running',
            'enhanced_analyzer': 'loaded' if ENHANCED_ANALYZER else 'not_loaded',
            'suggestion_engine': 'loaded' if SUGGESTION_ENGINE else 'not_loaded',
            'behavior_tracker': 'loaded' if BEHAVIOR_TRACKER else 'not_loaded',
            'analytics': 'loaded',
            'export_system': 'loaded',
            'lexicon': f'{len(LEXICON.keywords)} words loaded'
        },
        'endpoints': {
            'prediction': '/predict',
            'chat_analyzer': '/chat-analyzer',
            'dashboard': '/live-dashboard',
            'analytics': '/analytics',
            'batch': '/batch',
            'comparison': '/comparison'
        },
        'database': {
            'toxicity_words': len(LEXICON.keywords),
            'categories': len(LEXICON.category_keywords),
            'chat_history': len(chat_history)
        }
    }
    
    return jsonify(health_status)

@app.route('/api/overview', methods=['GET'])
def api_overview():
  # datasets in data/datasets
  ds_dir = ROOT / 'data' / 'datasets'
  ds_files = []
  if ds_dir.exists():
    ds_files = [str(p.relative_to(ROOT)) for p in ds_dir.iterdir() if p.is_file()]
  models_dir = ROOT / 'models'
  model_dirs = [p.name for p in models_dir.iterdir() if p.is_dir()] if models_dir.exists() else []
  log_files = [str(p.relative_to(ROOT)) for p in (ROOT / 'data' / 'logs').glob('*.log')]
  return jsonify({
    'datasets': len(ds_files),
    'models': len(model_dirs),
    'logs': len(log_files),
    'dataset_files': ds_files,
    'model_dirs': model_dirs,
    'log_files': log_files,
    'lexicon_keywords': len(LEXICON.keywords),
    'lexicon_categories': len(LEXICON.category_keywords)
  })


@app.route('/api/models', methods=['GET'])
def api_models():
  models_dir = ROOT / 'models'
  models_dir.mkdir(parents=True, exist_ok=True)
  items = [p.name for p in models_dir.iterdir() if p.is_dir()]
  return jsonify({'models': items})


@app.route('/api/models/load', methods=['POST'])
def api_models_load():
  global ACTIVE_MODEL
  data = request.get_json() or {}
  name = data.get('name')
  if not name:
    return jsonify({'error': 'no name provided'}), 400
  path = ROOT / 'models' / name
  if not path.exists():
    return jsonify({'error': 'model not found'}), 404
  ACTIVE_MODEL = name
  return jsonify({'status': f'loaded {name}'})


@app.route('/api/models/delete', methods=['POST'])
def api_models_delete():
  import shutil
  data = request.get_json() or {}
  name = data.get('name')
  if not name:
    return jsonify({'error': 'no name provided'}), 400
  path = ROOT / 'models' / name
  if not path.exists():
    return jsonify({'error': 'model not found'}), 404
  shutil.rmtree(path)
  return jsonify({'status': f'deleted {name}'})


@app.route('/api/data-preview', methods=['GET'])
def api_data_preview():
  from urllib.parse import unquote
  import pandas as pd
  path = request.args.get('path')
  if not path:
    return jsonify({'error': 'path required'}), 400
  path = unquote(path)
  fp = ROOT / path
  if not fp.exists():
    return jsonify({'error': 'file not found'}), 404
  try:
    df = pd.read_csv(fp, nrows=200)
  except Exception as e:
    return jsonify({'error': f'failed to read csv: {e}'}), 500
  rows = df.fillna('').to_dict(orient='records')
  cols = list(df.columns)
  counts = {}
  if 'label' in df.columns:
    vc = df['label'].value_counts().to_dict()
    counts = {int(k): int(v) for k,v in vc.items()}
  return jsonify({'columns': cols, 'rows': rows, 'counts': counts})


@app.route('/api/jobs', methods=['GET'])
def api_jobs():
  out = []
  for jid, j in jobs.items():
    out.append({'id': jid, 'status': j.get('status'), 'log': j.get('log'), 'type': j.get('type', 'background')})
  # include recent logs from LOG_DIR
  for p in LOG_DIR.glob('*.log'):
    out.append({'id': p.name, 'status': 'file', 'log': str(p), 'type': 'logfile'})
  return jsonify({'jobs': out})


@app.route('/api/log', methods=['GET'])
def api_log():
  from urllib.parse import unquote
  p = request.args.get('path')
  if not p:
    return jsonify({'error': 'path required'}), 400
  p = unquote(p)
  fp = Path(p)
  if not fp.exists():
    return jsonify({'error': 'not found'}), 404
  try:
    txt = fp.read_text(errors='replace')
  except Exception as e:
    txt = f'failed to read log: {e}'
  return jsonify({'content': txt})


@app.route('/api/settings', methods=['POST'])
def api_settings():
  data = request.get_json() or {}
  # rudimentary: save to .env
  cfg_path = ROOT / '.env'
  lines = []
  if cfg_path.exists():
    lines = cfg_path.read_text().splitlines()
  kv = {k.split('=')[0]:k.split('=')[1] for k in lines if '=' in k}
  if 'spark_master' in data:
    kv['SPARK_MASTER'] = data['spark_master']
  if 'data_folder' in data:
    kv['DATA_FOLDER'] = data['data_folder']
  out = '\n'.join([f'{k}={v}' for k,v in kv.items()])
  cfg_path.write_text(out)
  return jsonify({'status':'saved','path':str(cfg_path)})


@app.route('/api/lexicon/reload', methods=['POST'])
def api_lexicon_reload():
  """Refresh the heuristic lexicon from the comprehensive dataset."""
  load_toxic_lexicon()
  return jsonify({
    'status': 'reloaded',
    'keywords': len(LEXICON.keywords),
    'categories': len(LEXICON.category_keywords)
  })


@app.route('/api/messages/dataset-analysis', methods=['GET'])
def api_dataset_analysis():
  """Analyze a dataset file with the heuristic scorer and return summary stats."""
  dataset_arg = request.args.get('path')
  limit_arg = request.args.get('limit', '500')
  try:
    limit = max(1, min(int(limit_arg), 5000))
  except ValueError:
    limit = 500

  if dataset_arg:
    dataset_path = Path(dataset_arg)
    if not dataset_path.is_absolute():
      dataset_path = (ROOT / dataset_arg).resolve()
  else:
    dataset_path = (ROOT / 'data' / 'datasets' / 'comprehensive_toxicity_dataset.csv').resolve()

  if not dataset_path.exists():
    return jsonify({'error': 'dataset not found', 'path': str(dataset_path)}), 404

  try:
    df = pd.read_csv(dataset_path, nrows=limit)
  except Exception as exc:
    return jsonify({'error': f'failed to read dataset: {exc}'}), 500

  if df.empty:
    return jsonify({
      'dataset': str(dataset_path),
      'analyzed': 0,
      'summary': summarize_messages([]),
      'label_breakdown': {},
      'highlights': {'high_risk': []}
    })

  # pick a sensible text column fallback
  text_col = None
  for candidate in ('text', 'comment_text', 'message', 'content'):
    if candidate in df.columns:
      text_col = candidate
      break
  if text_col is None:
    string_cols = df.select_dtypes(include=['object']).columns.tolist()
    text_col = string_cols[0] if string_cols else df.columns[0]

  label_breakdown = {}
  if 'label' in df.columns:
    vc = df['label'].fillna(0).value_counts().to_dict()
    label_breakdown = {str(k): int(v) for k, v in vc.items()}

  # Ensure lexicon is loaded
  if not LEXICON.keywords:
    load_toxic_lexicon()

  analyses = []
  for idx, row in df.iterrows():
    text = str(row.get(text_col, '') or '')
    report = heuristic_analyze_text(text)
    report['row_index'] = int(idx)
    report['text'] = text
    analyses.append(report)

  summary = summarize_messages(analyses)

  def build_highlight(records):
    items = []
    for entry in records:
      snippet = entry['text'][:200]
      if len(entry['text']) > 200:
        snippet += '…'
      items.append({
        'row_index': entry['row_index'],
        'toxicity_score': entry['toxicity_score'],
        'risk_level': entry['risk_level'],
        'top_category': entry['top_category'],
        'matched_keywords': entry['matched_keywords'],
        'text_snippet': snippet
      })
    return items

  high_sorted = sorted(analyses, key=lambda r: r['toxicity_score'], reverse=True)
  high_highlights = build_highlight(high_sorted[:10])

  dataset_display = (
    str(dataset_path.relative_to(ROOT))
    if str(dataset_path).startswith(str(ROOT))
    else str(dataset_path)
  )

  return jsonify({
    'dataset': dataset_display,
    'analyzed': len(analyses),
    'summary': summary,
    'label_breakdown': label_breakdown,
    'highlights': {
      'high_risk': high_highlights
    }
  })


@app.route('/api/help', methods=['GET'])
def api_help():
    p = ROOT / 'README.md'
    if not p.exists():
        return jsonify({'content': ''})
    return jsonify({'content': p.read_text(encoding='utf-8')})


# Innovative Chat Analysis Features
chat_history = []

@app.route('/api/chat/analyze', methods=['POST'])
def analyze_chat():
    """Analyze multiple messages at once for chat moderation"""
    data = request.get_json() or {}
    messages = data.get('messages', [])
    if not messages:
        return jsonify({'error': 'no messages provided'}), 400
    
    results = []
    for msg in messages:
        text = msg.get('text', '')
        if not text:
            continue

        heuristic = heuristic_analyze_text(text)
        result = {
            'message_id': msg.get('id', len(results)),
            'user': msg.get('user', 'unknown'),
            'text': text,
            'toxicity_score': heuristic['toxicity_score'],
            'risk_level': heuristic['risk_level'],
            'matched_keywords': heuristic['matched_keywords'],
            'top_category': heuristic['top_category'],
            'category_scores': heuristic['category_scores'],
  'confidence': heuristic['confidence'],
  'reference_example': heuristic.get('reference_example'),
            'timestamp': msg.get('timestamp', time.time())
        }
        results.append(result)
        chat_history.append(result)
    
    # Keep only last 100 messages
    if len(chat_history) > 100:
        chat_history[:] = chat_history[-100:]
    
    # Calculate chat room statistics
    avg_toxicity = sum(r['toxicity_score'] for r in results) / len(results) if results else 0
    high_risk_count = sum(1 for r in results if r['risk_level'] == 'HIGH')
    
    return jsonify({
        'analyzed_count': len(results),
        'results': results,
        'statistics': {
            'average_toxicity': avg_toxicity,
            'high_risk_messages': high_risk_count,
            'flagged_percentage': (high_risk_count / len(results) * 100) if results else 0
        }
    })


@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """Get recent chat analysis history with trends"""
    limit = int(request.args.get('limit', 50))
    recent_messages = chat_history[-limit:] if chat_history else []
    
    # Calculate trends
    if len(recent_messages) >= 10:
        recent_10 = recent_messages[-10:]
        prev_10 = recent_messages[-20:-10] if len(recent_messages) >= 20 else []
        
        recent_avg = sum(m['toxicity_score'] for m in recent_10) / len(recent_10)
        prev_avg = sum(m['toxicity_score'] for m in prev_10) / len(prev_10) if prev_10 else recent_avg
        trend = 'increasing' if recent_avg > prev_avg * 1.1 else 'decreasing' if recent_avg < prev_avg * 0.9 else 'stable'
    else:
        trend = 'insufficient_data'
        recent_avg = sum(m['toxicity_score'] for m in recent_messages) / len(recent_messages) if recent_messages else 0
    
    return jsonify({
        'messages': recent_messages,
        'trend': trend,
        'current_average': recent_avg,
        'total_analyzed': len(chat_history)
    })


@app.route('/api/chat/moderate', methods=['POST'])
def moderate_message():
  """Real-time message moderation with action recommendations and user tracking"""
  global ENHANCED_ANALYZER, BEHAVIOR_TRACKER
  
  data = request.get_json() or {}
  text = data.get('text', '')
  user = data.get('user', 'unknown')

  if not text:
    return jsonify({'error': 'no text provided'}), 400

  # Initialize analyzers
  if ENHANCED_ANALYZER is None:
    ENHANCED_ANALYZER = EnhancedToxicityAnalyzer()
  if BEHAVIOR_TRACKER is None:
    BEHAVIOR_TRACKER = UserBehaviorTracker()

  # Analyze with enhanced analyzer
  toxicity_result = ENHANCED_ANALYZER.analyze_text(text)
  score = toxicity_result['toxicity_score']
  risk_level = toxicity_result['toxicity_level']
  
  # Track user behavior
  user_profile = BEHAVIOR_TRACKER.track_message(user, text, toxicity_result)
  
  # Check if user is muted
  if BEHAVIOR_TRACKER.is_user_muted(user):
    return jsonify({
      'error': 'user_muted',
      'message': 'You are currently muted',
      'mute_until': user_profile['mute_until']
    }), 403

  # Get recommended actions from profile
  actions = user_profile.get('recommended_actions', [])
  
  # Add category-specific guidance
  category_guidance = {
    'threat': ['escalate_to_admin', 'notify_security'],
    'severe_toxic': ['escalate_to_admin', 'require_manual_review'],
    'identity_hate': ['escalate_to_admin', 'require_manual_review'],
    'violence': ['warn_user', 'review_required'],
    'sexual': ['warn_user', 'review_required'],
  }

  top_category = toxicity_result['top_category']
  if top_category and top_category in category_guidance:
    actions.extend(category_guidance[top_category])

  # Deduplicate actions
  actions = list(set(actions))

  result = {
    'text': text,
    'user': user,
    'toxicity_score': score,
    'risk_level': risk_level,
    'matched_keywords': [m['word'] for m in toxicity_result['matched_words']],
    'top_category': top_category,
    'category_breakdown': toxicity_result['category_breakdown'],
    'recommended_actions': actions,
    'user_profile': {
      'risk_score': user_profile['risk_score'],
      'risk_level': user_profile['risk_level'],
      'violation_count': user_profile['violation_count'],
      'strikes': user_profile['strikes'],
      'warnings': user_profile['warnings'],
      'behavior_patterns': user_profile['behavior_patterns']
    },
    'timestamp': time.time()
  }

  chat_history.append(result)
  if len(chat_history) > 100:
    chat_history[:] = chat_history[-100:]

  return jsonify(result)

@app.route('/api/chat/analyze-file', methods=['POST'])
def analyze_file():
  """Analyze uploaded chat dataset file (CSV or TXT)"""
  global ENHANCED_ANALYZER
  
  if ENHANCED_ANALYZER is None:
    ENHANCED_ANALYZER = EnhancedToxicityAnalyzer()
  
  # Check if file was uploaded
  if 'file' not in request.files:
    return jsonify({'error': 'No file uploaded'}), 400
  
  file = request.files['file']
  if file.filename == '':
    return jsonify({'error': 'No file selected'}), 400
  
  # Get analysis options
  depth = request.form.get('depth', 'standard')
  generate_charts = request.form.get('generateCharts', 'true').lower() == 'true'
  generate_report = request.form.get('generateReport', 'true').lower() == 'true'
  
  # Determine sample limit based on depth
  depth_limits = {
    'quick': 100,
    'standard': 500,
    'full': None  # No limit
  }
  limit = depth_limits.get(depth, 500)
  
  try:
    # Read file content
    import io
    import csv
    
    content = file.read().decode('utf-8')
    messages = []
    
    # Try to parse as CSV
    if file.filename.endswith('.csv'):
      csv_reader = csv.DictReader(io.StringIO(content))
      
      # Try to find message column
      possible_columns = ['message', 'text', 'content', 'chat', 'msg', 'comment', 'body']
      message_column = None
      
      for row in csv_reader:
        if message_column is None:
          # Find the message column
          for col in possible_columns:
            if col in [k.lower() for k in row.keys()]:
              message_column = [k for k in row.keys() if k.lower() == col][0]
              break
          
          if message_column is None:
            # Use first column as fallback
            message_column = list(row.keys())[0]
        
        if message_column in row:
          msg_text = row[message_column].strip()
          if msg_text:
            messages.append(msg_text)
            if limit and len(messages) >= limit:
              break
    
    else:
      # Parse as plain text (one message per line)
      lines = content.split('\n')
      for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):  # Skip comments
          messages.append(line)
          if limit and len(messages) >= limit:
            break
    
    if not messages:
      return jsonify({'error': 'No messages found in file'}), 400
    
    # Analyze all messages
    results = []
    category_counts = defaultdict(int)
    severity_counts = defaultdict(int)
    total_toxic = 0
    total_score = 0
    
    for i, message in enumerate(messages):
      analysis = ENHANCED_ANALYZER.analyze_text(message)
      
      is_toxic = analysis['toxicity_score'] > 30
      if is_toxic:
        total_toxic += 1
      
      total_score += analysis['toxicity_score']
      
      # Count categories
      if analysis['top_category']:
        category_counts[analysis['top_category']] += 1
      
      # Count severity
      severity_counts[analysis['toxicity_level']] += 1
      
      results.append({
        'message': message,
        'toxicity_score': analysis['toxicity_score'],
        'is_toxic': is_toxic,
        'toxicity_level': analysis['toxicity_level'],
        'category': analysis['top_category'],
        'severity': analysis['toxicity_level'],
        'matched_words': [m['word'] for m in analysis['matched_words'][:5]]  # First 5
      })
    
    # Calculate summary statistics
    total_messages = len(messages)
    toxic_percentage = (total_toxic / total_messages * 100) if total_messages > 0 else 0
    avg_score = total_score / total_messages if total_messages > 0 else 0
    
    response_data = {
      'summary': {
        'total_messages': total_messages,
        'toxic_messages': total_toxic,
        'clean_messages': total_messages - total_toxic,
        'toxic_percentage': toxic_percentage,
        'average_toxicity_score': avg_score,
        'dataset_info': {
          'filename': file.filename,
          'analysis_depth': depth,
          'messages_analyzed': len(messages)
        }
      },
      'category_distribution': dict(category_counts),
      'severity_distribution': dict(severity_counts),
      'detailed_results': results
    }
    
    return jsonify(response_data)
    
  except Exception as e:
    import traceback
    traceback.print_exc()
    return jsonify({'error': f'Failed to analyze file: {str(e)}'}), 500

@app.route('/api/user-profile/<user_id>', methods=['GET'])
def get_user_profile_endpoint(user_id):
  """Get detailed user profile"""
  global BEHAVIOR_TRACKER
  
  if BEHAVIOR_TRACKER is None:
    BEHAVIOR_TRACKER = UserBehaviorTracker()
  
  profile = BEHAVIOR_TRACKER.get_user_profile(user_id)
  return jsonify(profile)

@app.route('/api/community-stats', methods=['GET'])
def get_community_stats():
  """Get community-wide statistics"""
  global BEHAVIOR_TRACKER
  
  if BEHAVIOR_TRACKER is None:
    BEHAVIOR_TRACKER = UserBehaviorTracker()
  
  stats = BEHAVIOR_TRACKER.get_community_stats()
  return jsonify(stats)
@app.route('/predict', methods=['POST'])
def predict():
  global ENHANCED_ANALYZER
  
  payload = request.json or {}
  text = payload.get('text', '')
  if not text:
    return jsonify({'error': 'no text provided'}), 400

  # Initialize enhanced analyzer if not already done
  if ENHANCED_ANALYZER is None:
    ENHANCED_ANALYZER = EnhancedToxicityAnalyzer()
  
  # Use enhanced toxicity analysis
  result = ENHANCED_ANALYZER.analyze_text(text)
  
  # Log to analytics
  analytics.log_analysis(text, result)
  
  return jsonify({
      'text': text,
      'toxicity_score': result['toxicity_score'],
      'toxicity_level': result['toxicity_level'],
      'risk_level': result['toxicity_level'],  # Backward compatibility
      'matched_keywords': [m['word'] for m in result['matched_words']],
      'matched_words_detail': result['matched_words'],
      'total_matches': result['total_matches'],
      'top_category': result['top_category'],
      'category_breakdown': result['category_breakdown'],
      'severity_breakdown': result['severity_breakdown'],
      'max_severity': result['max_severity'],
      'avg_severity': result['avg_severity'],
      'toxicity_density': result['toxicity_density'],
      'warning_message': result['warning_message'],
      'note': 'Enhanced toxicity analysis using 2000+ word database with severity levels',
      'categories': result.get('category_breakdown', {})  # For comparison tool
  })

@app.route('/api/suggest-alternatives', methods=['POST'])
def suggest_alternatives_endpoint():
  """Get AI-powered suggestions for rephrasing toxic messages"""
  global ENHANCED_ANALYZER, SUGGESTION_ENGINE
  
  payload = request.json or {}
  text = payload.get('text', '')
  if not text:
    return jsonify({'error': 'no text provided'}), 400
  
  # Initialize analyzers
  if ENHANCED_ANALYZER is None:
    ENHANCED_ANALYZER = EnhancedToxicityAnalyzer()
  if SUGGESTION_ENGINE is None:
    SUGGESTION_ENGINE = ResponseSuggestionEngine()
  
  # Analyze toxicity first
  toxicity_result = ENHANCED_ANALYZER.analyze_text(text)
  
  # Get suggestions
  toxicity_info = {
    'toxicity_score': toxicity_result['toxicity_score'],
    'top_category': toxicity_result['top_category'],
    'matched_keywords': [m['word'] for m in toxicity_result['matched_words']]
  }
  
  suggestions = SUGGESTION_ENGINE.suggest_alternatives(text, toxicity_info)
  
  return jsonify({
      'original_analysis': toxicity_result,
      'suggestions': suggestions,
      'status': 'success'
  })

@app.route('/api/analyze-conversation', methods=['POST'])
def analyze_conversation_endpoint():
  """Analyze an entire conversation thread"""
  global SUGGESTION_ENGINE
  
  payload = request.json or {}
  messages = payload.get('messages', [])
  if not messages:
    return jsonify({'error': 'no messages provided'}), 400
  
  if SUGGESTION_ENGINE is None:
    SUGGESTION_ENGINE = ResponseSuggestionEngine()
  
  result = SUGGESTION_ENGINE.batch_analyze_conversation(messages)
  
  return jsonify(result)

# NEW ANALYTICS ENDPOINTS
@app.route('/api/analytics', methods=['GET'])
def get_analytics():
  """Get comprehensive analytics data"""
  days = int(request.args.get('days', 7))
  
  return jsonify({
    'trends': analytics.get_trends(days),
    'category_distribution': analytics.get_category_distribution(days),
    'peak_hours': analytics.get_peak_hours(),
    'statistics': analytics.get_statistics(),
    'insights': analytics.get_insights()
  })

@app.route('/api/dashboard/data', methods=['GET'])
def get_dashboard_data():
  """Get real-time dashboard data"""
  recent_messages = chat_history[-10:] if chat_history else []
  
  return jsonify({
    'recent_messages': recent_messages,
    'stats': analytics.get_statistics(),
    'timestamp': time.time()
  })

# NEW BATCH ANALYSIS & EXPORT ENDPOINTS
@app.route('/api/batch-analyze', methods=['POST'])
def batch_analyze():
  """Analyze multiple messages in batch"""
  payload = request.json or {}
  messages = payload.get('messages', [])
  
  if not messages:
    return jsonify({'error': 'no messages provided'}), 400
  
  results = export_system.analyze_batch(messages)
  summary = export_system.generate_summary(results)
  
  # Log each to analytics
  for result in results:
    analytics.log_analysis(result['full_text'], result)
  
  return jsonify({
    'results': results,
    'summary': summary,
    'total': len(results)
  })

@app.route('/upload-dataset', methods=['POST'])
def upload_dataset():
  """Upload and analyze chat message dataset"""
  global ENHANCED_ANALYZER
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
    
    # Ensure lexicon and analyzer are loaded
    if not LEXICON.keywords:
      load_toxic_lexicon()
    
    if ENHANCED_ANALYZER is None:
      ENHANCED_ANALYZER = EnhancedToxicityAnalyzer()
    
    # Analyze messages (limit to 500 for performance)
    results = []
    for idx, row in df.head(500).iterrows():
      message = str(row[message_col])
      if message and len(message.strip()) > 0:
        # Basic analysis
        basic_result = heuristic_analyze_text(message)
        
        # Enhanced analysis
        try:
          enhanced_result = ENHANCED_ANALYZER.analyze_text(message)
          toxicity_score = enhanced_result.get('toxicity_probability', basic_result['toxicity_score'])
          is_toxic = enhanced_result.get('is_toxic', toxicity_score > 0.5)
          categories = enhanced_result.get('categories', [basic_result.get('top_category', 'general')])
          severity = enhanced_result.get('severity', 'low' if toxicity_score < 0.4 else 'medium' if toxicity_score < 0.7 else 'high')
        except:
          # Fallback to basic analysis
          toxicity_score = basic_result['toxicity_score']
          is_toxic = toxicity_score > 0.5
          categories = [basic_result.get('top_category', 'general')] if basic_result.get('top_category') else []
          severity = 'low' if toxicity_score < 0.4 else 'medium' if toxicity_score < 0.7 else 'high'
        
        results.append({
          'index': int(idx),
          'message': message[:200] + '...' if len(message) > 200 else message,
          'toxicity_score': float(toxicity_score),
          'is_toxic': bool(is_toxic),
          'categories': categories,
          'severity': severity
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
      'results': results,
      'message': f'Successfully analyzed {total_messages} messages from dataset'
    })
    
  except Exception as e:
    import traceback
    traceback.print_exc()
    return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/datasets/list', methods=['GET'])
def list_datasets():
  """List all available sample datasets"""
  try:
    catalog_path = ROOT / 'data' / 'sample_datasets' / 'catalog.json'
    
    if catalog_path.exists():
      with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
      return jsonify(catalog)
    else:
      return jsonify({'datasets': []})
      
  except Exception as e:
    return jsonify({'error': str(e)}), 500

@app.route('/api/datasets/analyze', methods=['POST'])
def analyze_dataset_api():
  """Analyze a specific dataset"""
  global ENHANCED_ANALYZER
  try:
    data = request.json
    dataset_id = data.get('dataset_id')
    
    if not dataset_id:
      return jsonify({'error': 'No dataset_id provided'}), 400
    
    # Load dataset
    dataset_path = ROOT / 'data' / 'sample_datasets' / f'{dataset_id}.csv'
    
    if not dataset_path.exists():
      return jsonify({'error': 'Dataset not found'}), 404
    
    # Read CSV
    df = pd.read_csv(dataset_path)
    
    # Find message column
    message_col = None
    for col in ['message', 'text', 'content', 'chat', 'msg']:
      if col in df.columns:
        message_col = col
        break
    
    if not message_col:
      text_cols = df.select_dtypes(include=['object']).columns
      if len(text_cols) > 0:
        message_col = text_cols[0]
      else:
        return jsonify({'error': 'No text column found'}), 400
    
    # Ensure analyzer is loaded
    if not LEXICON.keywords:
      load_toxic_lexicon()
    
    if ENHANCED_ANALYZER is None:
      ENHANCED_ANALYZER = EnhancedToxicityAnalyzer()
    
    # Analyze messages
    results = []
    toxic_count = 0
    total_toxicity = 0
    
    for idx, row in df.iterrows():
      message = str(row[message_col])
      if message and len(message.strip()) > 0:
        # Basic analysis
        basic_result = heuristic_analyze_text(message)
        
        # Enhanced analysis
        try:
          enhanced_result = ENHANCED_ANALYZER.analyze_text(message)
          toxicity_score = enhanced_result.get('toxicity_probability', basic_result['toxicity_score'])
          is_toxic = enhanced_result.get('is_toxic', toxicity_score > 0.5)
        except:
          toxicity_score = basic_result['toxicity_score']
          is_toxic = toxicity_score > 0.5
        
        if is_toxic:
          toxic_count += 1
        total_toxicity += toxicity_score
        
        results.append({
          'message': message[:100],
          'toxicity_score': float(toxicity_score),
          'is_toxic': bool(is_toxic)
        })
    
    total_messages = len(results)
    avg_toxicity = total_toxicity / total_messages if total_messages > 0 else 0
    
    analysis = {
      'total_messages': total_messages,
      'toxic_messages': toxic_count,
      'average_toxicity_score': avg_toxicity,
      'messages': results[:10]  # Return first 10 for preview
    }
    
    return jsonify({
      'status': 'success',
      'dataset_id': dataset_id,
      'analysis': analysis
    })
    
  except Exception as e:
    import traceback
    traceback.print_exc()
    return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/export', methods=['POST'])
def export_results():
  """Export analysis results in various formats"""
  payload = request.json or {}
  results = payload.get('results', [])
  format_type = payload.get('format', 'csv')
  
  if not results:
    return jsonify({'error': 'no results to export'}), 400
  
  if format_type == 'csv':
    content = export_system.export_to_csv(results)
    mimetype = 'text/csv'
    filename = 'toxicity_analysis.csv'
  elif format_type == 'json':
    content = export_system.export_to_json(results)
    mimetype = 'application/json'
    filename = 'toxicity_analysis.json'
  elif format_type == 'html':
    content = export_system.generate_html_report(results)
    mimetype = 'text/html'
    filename = 'toxicity_report.html'
  else:
    return jsonify({'error': 'unsupported format'}), 400
  
  return Response(
    content,
    mimetype=mimetype,
    headers={
      'Content-Disposition': f'attachment; filename={filename}'
    }
  )

@app.route('/static/<path:p>')
def static_files(p):
  return send_from_directory(str(ROOT / 'static'), p)

# Spark UI Management Routes
@app.route('/spark-status')
def spark_status():
    """Get Spark UI status"""
    is_running = is_spark_ui_running()
    return jsonify({
        'running': is_running,
        'url': 'http://localhost:4040' if is_running else None,
        'proxy_url': '/spark-proxy/' if is_running else None
    })

@app.route('/spark-start', methods=['POST'])
def spark_start():
    """Manually start Spark UI"""
    try:
        if is_spark_ui_running():
            return jsonify({'status': 'already_running', 'message': 'Spark UI is already running'})
        
        if start_spark_ui():
            return jsonify({'status': 'started', 'message': 'Spark UI started successfully', 'url': 'http://localhost:4040'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to start Spark UI'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/spark-stop', methods=['POST'])
def spark_stop():
    """Manually stop Spark UI"""
    try:
        stop_spark_ui()
        return jsonify({'status': 'stopped', 'message': 'Spark UI stopped successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/spark-run-direct', methods=['POST'])
def spark_run_direct():
    """
    Run a Spark job directly using the persistent Spark session.
    This ensures the job appears in the Spark Web UI.
    """
    try:
        import threading
        from spark_manager import get_spark_session
        
        data = request.get_json() or {}
        input_path = data.get('input', 'data/datasets/comprehensive_toxicity_dataset.csv')
        output_path = data.get('output', 'data/processed/direct_spark_output.parquet')
        
        # Ensure Spark UI is running
        if not is_spark_ui_running():
            print("[*] Starting Spark UI for job...")
            start_spark_ui()
            time.sleep(2)  # Give it time to start
        
        # Get the persistent Spark session
        spark = get_spark_session()
        if not spark:
            return jsonify({'status': 'error', 'message': 'Spark session not initialized'}), 500
        
        job_id = f"direct_job_{int(time.time())}"
        
        def run_job_async():
            """Run the Spark job in a background thread"""
            try:
                print(f"[*] Starting direct Spark job {job_id}...")
                print(f"[*] Input: {input_path}")
                print(f"[*] Output: {output_path}")
                
                # Read the CSV
                df = spark.read.csv(input_path, header=True, inferSchema=True)
                row_count = df.count()
                print(f"[+] Read {row_count} rows from {input_path}")
                
                # Perform some transformations (creates stages in UI)
                print("[*] Running transformations...")
                
                # Add a processing column
                from pyspark.sql.functions import col, length, lower, when
                df_processed = df.withColumn("text_length", length(col("text"))) \
                                 .withColumn("text_lower", lower(col("text")))
                
                # Filter and aggregate (more stages)
                df_filtered = df_processed.filter(col("text_length") > 5)
                filtered_count = df_filtered.count()
                print(f"[+] Filtered to {filtered_count} rows")
                
                # Write to parquet (creates more stages)
                print(f"[*] Writing to {output_path}...")
                df_filtered.write.mode("overwrite").parquet(output_path)
                
                print(f"[+] Job {job_id} completed successfully!")
                print(f"[+] Output saved to: {output_path}")
                
            except Exception as e:
                print(f"[!] Job {job_id} failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Start job in background thread
        job_thread = threading.Thread(target=run_job_async, daemon=True)
        job_thread.start()
        
        return jsonify({
            'status': 'started',
            'job_id': job_id,
            'spark_ui_url': 'http://localhost:4040',
            'spark_ui_proxy': '/spark-proxy/',
            'spark_ui_status': 'running',
            'message': f'Direct Spark job {job_id} started. Check Spark UI for real-time progress.'
        })
        
    except Exception as e:
        import traceback
        return jsonify({'status': 'error', 'message': str(e), 'trace': traceback.format_exc()}), 500

# Proxy Spark UI requests to avoid iframe X-Frame issues. Local-only helper.
SPARK_UI_BASE = 'http://localhost:4040'

@app.route('/spark-proxy/', defaults={'subpath': ''})
@app.route('/spark-proxy/<path:subpath>')
def spark_proxy(subpath):
    """
    Forwards GET requests to the Spark UI.
    Provides a helpful message if the Spark UI is not available.
    """
    try:
        # Check if persistent Spark UI is running
        is_spark_active = is_spark_ui_running()
        
        # Also check if any jobs are running
        has_running_jobs = any(job.get('status') == 'running' for job in jobs.values())
        
        if not is_spark_active:
            # Try direct connection as final fallback
            try:
                response = requests.get(SPARK_UI_BASE, timeout=2)
                is_spark_active = response.status_code == 200
            except (requests.exceptions.RequestException, Exception):
                # Silently fail if Spark UI is not available
                is_spark_active = False

        if not is_spark_active:
            return '''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Spark UI Not Available</title>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <style>
                        * { margin: 0; padding: 0; box-sizing: border-box; }
                        body { 
                            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; 
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            min-height: 100vh;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            padding: 20px;
                        }
                        .container { 
                            max-width: 600px;
                            background: white;
                            border-radius: 16px;
                            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                            padding: 50px;
                            text-align: center;
                        }
                        .icon { font-size: 64px; margin-bottom: 20px; }
                        h2 { color: #333; margin-bottom: 20px; font-size: 28px; }
                        p { color: #666; line-height: 1.8; margin-bottom: 30px; font-size: 16px; }
                        .btn { 
                            display: inline-block;
                            padding: 14px 32px;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            text-decoration: none;
                            border-radius: 8px;
                            font-weight: 600;
                            transition: transform 0.2s, box-shadow 0.2s;
                            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                        }
                        .btn:hover { 
                            transform: translateY(-2px);
                            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
                        }
                        .info { 
                            background: #f8f9fa;
                            border-radius: 8px;
                            padding: 20px;
                            margin: 30px 0;
                            text-align: left;
                        }
                        .info strong { color: #667eea; display: block; margin-bottom: 10px; }
                        .info ul { margin-left: 20px; }
                        .info li { margin: 8px 0; color: #555; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="icon">⚡</div>
                        <h2>Spark UI Not Running</h2>
                        <p>The Apache Spark UI is not currently active. No worries! Your main application works perfectly without it.</p>
                        <div class="info">
                            <strong>ℹ️ What is Spark UI?</strong>
                            <ul>
                                <li>Optional monitoring interface for Spark jobs</li>
                                <li>Only needed when running data processing tasks</li>
                                <li>Your toxicity analyzer works independently</li>
                            </ul>
                        </div>
                        <a href="/" class="btn">← Back to Main App</a>
                    </div>
                </body>
                </html>
            ''', 503

        # If Spark is active, try to proxy the request
        url = f"{SPARK_UI_BASE}/{subpath}" if subpath else SPARK_UI_BASE + '/'
        
        # Try to connect with shorter timeout to fail fast
        response = requests.get(url, stream=True, timeout=5, params=request.args, allow_redirects=True)
        
        if response.status_code != 200:
            # If we get an error status, show friendly message
            raise requests.exceptions.ConnectionError("Spark UI returned error status")
        
        content_type = response.headers.get('Content-Type', 'text/html')
        
        # Stream the response content
        return Response(
            response.iter_content(chunk_size=10*1024), 
            content_type=content_type, 
            status=response.status_code,
            headers={
                'Cache-Control': 'no-cache',
                'X-Content-Type-Options': 'nosniff'
            }
        )

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        # Redirect to home with a message instead of showing error
        return '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Redirecting...</title>
                <meta http-equiv="refresh" content="0;url=/">
                <style>
                    body { 
                        font-family: system-ui, -apple-system, sans-serif; 
                        display: flex; 
                        align-items: center; 
                        justify-content: center; 
                        height: 100vh; 
                        margin: 0;
                        background: #f5f5f5;
                    }
                    .message { 
                        text-align: center; 
                        padding: 40px;
                        background: white;
                        border-radius: 8px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }
                    h2 { color: #666; margin: 0 0 10px 0; }
                    p { color: #999; }
                </style>
            </head>
            <body>
                <div class="message">
                    <h2>Spark UI Not Available</h2>
                    <p>Redirecting to main application...</p>
                </div>
            </body>
            </html>
        ''', 302
    except Exception as e:
        # Log the error but don't show it to user
        print(f"Spark proxy error: {e}")
        return '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Redirecting...</title>
                <meta http-equiv="refresh" content="0;url=/">
                <style>
                    body { 
                        font-family: system-ui, -apple-system, sans-serif; 
                        display: flex; 
                        align-items: center; 
                        justify-content: center; 
                        height: 100vh; 
                        margin: 0;
                        background: #f5f5f5;
                    }
                    .message { 
                        text-align: center; 
                        padding: 40px;
                        background: white;
                        border-radius: 8px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }
                </style>
            </head>
            <body>
                <div class="message">
                    <h2>🔄 Redirecting...</h2>
                    <p>Taking you back to the main application</p>
                </div>
            </body>
            </html>
        ''', 302


if __name__ == '__main__':
  # ensure working directory is project root
  os.chdir(ROOT)
  
  print("[*] Starting Enhanced Toxicity Analysis Server...")
  print("[*] Toxicity Detection System Ready")
  print(f"[*] Loaded {len(LEXICON.keywords)} toxicity keywords")
  
  # Auto-start Spark UI for immediate availability
  print("\n[*] Initializing Apache Spark Web UI...")
  try:
    if start_spark_ui():
      print("  [+] Spark Web UI started successfully")
      print("  [*] Access at: http://localhost:4040")
      print("  [*] Spark session ready for data processing")
    else:
      print("  [!] Spark UI start failed (will be available when jobs run)")
  except Exception as e:
    print(f"  [!] Spark UI initialization skipped: {e}")
  
  print("\n[*] Application Endpoints:")
  print("  [+] Main Dashboard: http://127.0.0.1:5000")
  print("  [+] Chat Analyzer: http://127.0.0.1:5000/chat-analyzer")
  print("  [+] Live Dashboard: http://127.0.0.1:5000/live-dashboard")
  print("  [+] Dataset Analyzer: http://127.0.0.1:5000/dataset-analyzer")
  print("  [+] Comparison: http://127.0.0.1:5000/comparison")
  print("  [+] Analytics: http://127.0.0.1:5000/analytics")
  print("  [+] Spark Web UI: http://localhost:4040")
  print("")

  try:
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
  except KeyboardInterrupt:
    print("\n[*] Shutting down gracefully...")
  finally:
    # Gracefully stop Spark UI if running
    try:
      if spark_manager.spark:
        print("[*] Stopping Spark Web UI...")
        stop_spark_ui()
        print("  [+] Spark UI stopped successfully")
    except Exception as e:
      print(f"  [!] Error stopping Spark UI: {e}")
    print("[*] Server shutdown complete")