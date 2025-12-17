async function api(path, opts) {
  const res = await fetch(path, opts);
  return res.json();
}

// Main predict functionality
document.getElementById('predict-btn').addEventListener('click', async () => {
  const text = document.getElementById('predict-text').value;
  
  if (!text.trim()) {
    document.getElementById('predict-result').innerHTML = '<strong>Error:</strong> Please enter a message to analyze';
    return;
  }
  
  // Show loading state
  document.getElementById('predict-result').innerHTML = '<em>Analyzing...</em>';
  
  try {
    const r = await api('/predict', {method: 'POST', body: JSON.stringify({text}), headers: {'Content-Type': 'application/json'}});
    
    const resultDiv = document.getElementById('predict-result');
    const riskDiv = document.getElementById('risk-indicator');
    
    if (r.error) {
      resultDiv.innerHTML = `<strong>Error:</strong> ${r.error}`;
      return;
    }
    
    const score = r.toxicity_score ? r.toxicity_score.toFixed(1) : '0.0';
    const riskLevel = r.toxicity_level || r.risk_level || 'SAFE';
    const totalMatches = r.total_matches || 0;
    
    const keywords = (r.matched_keywords && r.matched_keywords.length)
      ? r.matched_keywords.slice(0, 10).join(', ')
      : 'None detected';

    const topCategory = r.top_category ? r.top_category.replace(/_/g, ' ').toUpperCase() : 'NONE';

    const categoryBreakdown = r.category_breakdown
      ? Object.entries(r.category_breakdown)
          .sort((a, b) => b[1] - a[1])
          .slice(0, 4)
          .map(([cat, score]) => `${cat.replace(/_/g, ' ')} (${score.toFixed(1)})`)
          .join(', ')
      : '';

    const severityInfo = r.max_severity 
      ? `<br><strong>Max Severity:</strong> ${r.max_severity}/5 | <strong>Avg:</strong> ${r.avg_severity}/5 | <strong>Density:</strong> ${r.toxicity_density}%`
      : '';

    const warningMsg = r.warning_message 
      ? `<div style="margin-top:10px;padding:10px;background:#fef3c7;border-left:4px solid #f59e0b;border-radius:4px;"><strong>${r.warning_message}</strong></div>`
      : '';

    resultDiv.innerHTML = `
      <strong>Toxicity Score:</strong> ${score}/100<br>
      <strong>Toxicity Level:</strong> <span style="font-weight:bold;color:${getRiskColor(riskLevel)}">${riskLevel}</span><br>
      <strong>Toxic Words Found:</strong> ${totalMatches}<br>
      <strong>Matched Keywords:</strong> ${keywords}<br>
      <strong>Top Category:</strong> ${topCategory}${categoryBreakdown ? `<br><strong>Category Breakdown:</strong> ${categoryBreakdown}` : ''}
      ${severityInfo}
      ${warningMsg}
      ${r.note ? `<br><small style="color:#6b7280;">${r.note}</small>` : ''}
    `;
    
    // Visual risk indicator
    const color = getRiskColor(riskLevel);
    
    riskDiv.innerHTML = `
      <div style="width:100%;height:10px;background:#e5e7eb;border-radius:5px;margin-top:10px;">
        <div style="width:${Math.min(score, 100)}%;height:100%;background:${color};border-radius:5px;transition:width 0.3s;"></div>
      </div>
    `;
  } catch (error) {
    document.getElementById('predict-result').innerHTML = `<strong>Error:</strong> Unable to connect to backend. ${error.message}`;
  }
});

function getRiskColor(level) {
  const colors = {
    'SAFE': '#10b981',
    'LOW': '#84cc16',
    'MEDIUM': '#f59e0b',
    'HIGH': '#f97316',
    'SEVERE': '#ef4444',
    'EXTREME': '#dc2626'
  };
  return colors[level] || '#6b7280';
}

// AI Suggestions functionality
document.getElementById('suggest-btn')?.addEventListener('click', async () => {
  const text = document.getElementById('predict-text').value;
  
  if (!text.trim()) {
    alert('Please enter a message first');
    return;
  }
  
  const suggestPanel = document.getElementById('suggestions-panel');
  const suggestContent = document.getElementById('suggestions-content');
  
  suggestPanel.style.display = 'block';
  suggestContent.innerHTML = '<em>Generating AI suggestions...</em>';
  
  try {
    const r = await api('/api/suggest-alternatives', {
      method: 'POST',
      body: JSON.stringify({text}),
      headers: {'Content-Type': 'application/json'}
    });
    
    if (r.error) {
      suggestContent.innerHTML = `<strong>Error:</strong> ${r.error}`;
      return;
    }
    
    const suggestions = r.suggestions;
    let html = '';
    
    // Recommended Action
    html += `<div style="padding: 12px; background: ${suggestions.recommended_action.includes('BLOCK') ? '#fee2e2' : suggestions.recommended_action.includes('REVIEW') ? '#fef3c7' : '#dbeafe'}; border-radius: 8px; margin-bottom: 15px;">`;
    html += `<strong style="color: #1e40af;">⚡ Recommended Action:</strong> ${suggestions.recommended_action}`;
    html += `</div>`;
    
    // Rephrase Options
    if (suggestions.rephrase_options && suggestions.rephrase_options.length > 0) {
      html += `<div style="margin-bottom: 15px;">`;
      html += `<strong style="color: #1e40af;">✨ Suggested Rephrases:</strong>`;
      html += `<div style="margin-top: 10px;">`;
      suggestions.rephrase_options.forEach((opt, i) => {
        html += `<div style="padding: 10px; background: white; border: 1px solid #bfdbfe; border-radius: 6px; margin-bottom: 8px; cursor: pointer; transition: all 0.2s;" 
                      onclick="document.getElementById('predict-text').value = this.textContent.trim(); this.style.background = '#dbeafe';"
                      onmouseover="this.style.background = '#eff6ff';"
                      onmouseout="this.style.background = 'white';">
                 ${opt}
                 </div>`;
      });
      html += `</div></div>`;
    }
    
    // Constructive Suggestions
    if (suggestions.suggestions && suggestions.suggestions.length > 0) {
      html += `<div style="margin-bottom: 15px;">`;
      html += `<strong style="color: #1e40af;">💡 Alternative Approaches:</strong>`;
      html += `<ul style="margin: 10px 0; padding-left: 20px;">`;
      suggestions.suggestions.forEach(sug => {
        html += `<li style="margin: 5px 0; color: #374151;">${sug}</li>`;
      });
      html += `</ul></div>`;
    }
    
    // Improvement Tips
    if (suggestions.improvement_tips && suggestions.improvement_tips.length > 0) {
      html += `<div style="margin-bottom: 15px;">`;
      html += `<strong style="color: #1e40af;">📚 Communication Tips:</strong>`;
      html += `<ul style="margin: 10px 0; padding-left: 20px;">`;
      suggestions.improvement_tips.forEach(tip => {
        html += `<li style="margin: 5px 0; color: #374151;">${tip}</li>`;
      });
      html += `</ul></div>`;
    }
    
    // Guidance
    if (suggestions.guidance && suggestions.guidance.length > 0) {
      html += `<div style="padding: 10px; background: white; border-left: 4px solid #3b82f6; border-radius: 4px;">`;
      html += `<strong style="color: #1e40af;">💬 Guidance:</strong><br>`;
      suggestions.guidance.forEach(g => {
        html += `<div style="margin-top: 5px; font-size: 14px; color: #6b7280;">• ${g}</div>`;
      });
      html += `</div>`;
    }
    
    suggestContent.innerHTML = html;
    
  } catch (error) {
    suggestContent.innerHTML = `<strong>Error:</strong> Unable to generate suggestions. ${error.message}`;
  }
});

// Spark Control Functions
let currentSparkJobId = null;
let sparkStatusInterval = null;
let sparkUIStatusInterval = null;

// Spark UI Control
async function checkSparkUIStatus() {
  try {
    const response = await api('/spark-status');
    const statusDiv = document.getElementById('spark-ui-status');
    const startBtn = document.getElementById('start-spark-ui-btn');
    const stopBtn = document.getElementById('stop-spark-ui-btn');
    const openLink = document.getElementById('open-spark-ui-link');
    
    if (response.is_running) {
      statusDiv.innerHTML = '<i class="fa fa-circle" style="color: #10b981;"></i> <span style="color: #10b981;">Running</span>';
      startBtn.disabled = true;
      stopBtn.disabled = false;
      openLink.style.pointerEvents = 'auto';
      openLink.style.opacity = '1';
    } else {
      statusDiv.innerHTML = '<i class="fa fa-circle" style="color: #ef4444;"></i> <span style="color: #ef4444;">Stopped</span>';
      startBtn.disabled = false;
      stopBtn.disabled = true;
      openLink.style.pointerEvents = 'none';
      openLink.style.opacity = '0.5';
    }
  } catch (error) {
    console.error('Error checking Spark UI status:', error);
    const statusDiv = document.getElementById('spark-ui-status');
    statusDiv.innerHTML = '<i class="fa fa-exclamation-triangle" style="color: #f59e0b;"></i> <span style="color: #f59e0b;">Unknown</span>';
  }
}

document.getElementById('start-spark-ui-btn')?.addEventListener('click', async () => {
  const btn = document.getElementById('start-spark-ui-btn');
  const resultDiv = document.getElementById('spark-control-result');
  
  btn.disabled = true;
  btn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Starting...';
  resultDiv.style.display = 'block';
  resultDiv.innerHTML = '<em>Starting Spark Web UI...</em>';
  
  try {
    const response = await api('/spark-start', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'}
    });
    
    if (response.status === 'started') {
      resultDiv.innerHTML = `
        <div style="padding: 15px; background: #dcfce7; border-radius: 8px; border: 1px solid #10b981;">
          <strong style="color: #15803d;">✅ ${response.message}</strong><br>
          <span style="font-size: 14px; color: #6b7280;">Web UI URL: ${response.url}</span>
        </div>
      `;
      setTimeout(() => {
        checkSparkUIStatus();
      }, 2000);
    } else if (response.status === 'already_running') {
      resultDiv.innerHTML = `
        <div style="padding: 15px; background: #dbeafe; border-radius: 8px; border: 1px solid #3b82f6;">
          <strong style="color: #1e40af;">ℹ️ ${response.message}</strong>
        </div>
      `;
      checkSparkUIStatus();
    } else {
      throw new Error(response.message || 'Failed to start Spark UI');
    }
  } catch (error) {
    resultDiv.innerHTML = `
      <div style="padding: 15px; background: #fee2e2; border-radius: 8px; border: 1px solid #ef4444;">
        <strong style="color: #dc2626;">❌ Error Starting Spark UI</strong><br>
        <span style="font-size: 14px; color: #6b7280;">${error.message}</span>
      </div>
    `;
  }
  
  btn.disabled = false;
  btn.innerHTML = '<i class="fa fa-play"></i> Start Spark UI';
});

document.getElementById('stop-spark-ui-btn')?.addEventListener('click', async () => {
  const btn = document.getElementById('stop-spark-ui-btn');
  const resultDiv = document.getElementById('spark-control-result');
  
  btn.disabled = true;
  btn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Stopping...';
  resultDiv.style.display = 'block';
  resultDiv.innerHTML = '<em>Stopping Spark Web UI...</em>';
  
  try {
    const response = await api('/spark-stop', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'}
    });
    
    resultDiv.innerHTML = `
      <div style="padding: 15px; background: #dbeafe; border-radius: 8px; border: 1px solid #3b82f6;">
        <strong style="color: #1e40af;">🛑 ${response.message}</strong>
      </div>
    `;
    
    setTimeout(() => {
      checkSparkUIStatus();
    }, 1000);
    
  } catch (error) {
    resultDiv.innerHTML = `
      <div style="padding: 15px; background: #fee2e2; border-radius: 8px; border: 1px solid #ef4444;">
        <strong style="color: #dc2626;">❌ Error Stopping Spark UI</strong><br>
        <span style="font-size: 14px; color: #6b7280;">${error.message}</span>
      </div>
    `;
  }
  
  btn.disabled = false;
  btn.innerHTML = '<i class="fa fa-stop"></i> Stop Spark UI';
});

document.getElementById('refresh-spark-status-btn')?.addEventListener('click', () => {
  checkSparkUIStatus();
});

// Auto-check Spark UI status on page load
if (document.getElementById('spark-ui-status')) {
  checkSparkUIStatus();
  // Auto-refresh every 10 seconds
  sparkUIStatusInterval = setInterval(checkSparkUIStatus, 10000);
}

// Direct Spark Job - Uses persistent session (jobs visible in UI)
document.getElementById('run-spark-direct-btn')?.addEventListener('click', async () => {
  const btn = document.getElementById('run-spark-direct-btn');
  const resultDiv = document.getElementById('spark-result');
  
  btn.disabled = true;
  btn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Running...';
  
  try {
    const response = await api('/spark-run-direct', {
      method: 'POST',
      body: JSON.stringify({
        input: 'data/datasets/comprehensive_toxicity_dataset.csv',
        output: 'data/processed/direct_spark_output.parquet'
      }),
      headers: {'Content-Type': 'application/json'}
    });
    
    if (response.error) {
      throw new Error(response.error);
    }
    
    resultDiv.innerHTML = `
      <div style="padding: 15px; background: #dbeafe; border-radius: 8px; border: 1px solid #3b82f6;">
        <strong style="color: #1e40af;">✅ ${response.message || 'Direct Spark Job Started'}</strong><br>
        <span style="font-size: 14px; color: #6b7280;">Job ID: ${response.job_id}</span><br>
        <span style="font-size: 14px; color: #6b7280;">Spark UI Status: ${response.spark_ui_status}</span><br>
        <div style="margin-top: 15px; padding: 12px; background: #fff; border-radius: 6px; border: 1px solid #93c5fd;">
          <strong style="color: #1e40af;">📊 Monitor Job in Real-Time:</strong><br>
          <div style="margin-top: 10px; display: flex; gap: 10px; flex-wrap: wrap;">
            <a href="${response.spark_ui_proxy}" target="_blank" class="btn" style="background: #6366f1; color: white; text-decoration: none; padding: 8px 16px; border-radius: 4px; font-size: 14px;">
              <i class="fa fa-external-link-alt"></i> Open Spark UI
            </a>
            <a href="${response.spark_ui_url}" target="_blank" class="btn ghost" style="padding: 8px 16px; border-radius: 4px; font-size: 14px;">
              <i class="fa fa-external-link-alt"></i> Direct Link
            </a>
          </div>
        </div>
        <div style="margin-top: 12px; padding: 10px; background: #d1fae5; border-radius: 6px; border-left: 3px solid #10b981;">
          <small style="color: #065f46;">
            <i class="fa fa-check-circle"></i> 
            <strong>Success!</strong> This job runs on the persistent Spark session, so you'll see it live in the Spark UI.
            Check the "Jobs" tab to see stages and tasks in real-time!
          </small>
        </div>
      </div>
    `;
    
    // Auto-open Spark UI
    if (response.spark_ui_status === 'running') {
      setTimeout(() => {
        window.open(response.spark_ui_proxy, 'SparkUI', 'width=1200,height=800');
      }, 1000);
    }
    
  } catch (error) {
    resultDiv.innerHTML = `
      <div style="padding: 15px; background: #fee2e2; border-radius: 8px; border: 1px solid #ef4444;">
        <strong style="color: #dc2626;">❌ Error Running Job</strong><br>
        <span style="font-size: 14px; color: #6b7280;">${error.message}</span>
      </div>
    `;
  }
  
  btn.disabled = false;
  btn.innerHTML = '<i class="fa fa-bolt"></i> Run Direct Spark Job';
});

document.getElementById('run-spark-btn')?.addEventListener('click', async () => {
  const btn = document.getElementById('run-spark-btn');
  const resultDiv = document.getElementById('spark-result');
  const statusSpan = document.getElementById('spark-status');
  
  btn.disabled = true;
  btn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Starting Spark...';
  if (statusSpan) statusSpan.innerHTML = '<span style="color: #f59e0b;">Starting...</span>';
  
  try {
    // Run Spark job with keep-alive to maintain UI access
    const response = await api('/run-spark', {
      method: 'POST',
      body: JSON.stringify({
        input: 'data/datasets/comprehensive_toxicity_dataset.csv',
        output: 'data/processed/spark_output.parquet',
        num_partitions: 4,
        keep_alive: 60  // Keep Spark UI alive for 60 seconds
      }),
      headers: {'Content-Type': 'application/json'}
    });
    
    if (response.error) {
      throw new Error(response.error);
    }
    
    currentSparkJobId = response.job_id;
    resultDiv.innerHTML = `
      <div style="padding: 15px; background: #dbeafe; border-radius: 8px; border: 1px solid #3b82f6;">
        <strong style="color: #1e40af;">✅ ${response.message || 'Spark Job Started'}</strong><br>
        <span style="font-size: 14px; color: #6b7280;">Job ID: ${response.job_id}</span><br>
        <span style="font-size: 14px; color: #6b7280;">Spark UI Status: ${response.spark_ui_status}</span><br>
        <div style="margin-top: 15px; padding: 12px; background: #fff; border-radius: 6px; border: 1px solid #93c5fd;">
          <strong style="color: #1e40af;">📊 Monitor Your Job:</strong><br>
          <div style="margin-top: 10px; display: flex; gap: 10px; flex-wrap: wrap;">
            <a href="${response.spark_ui_proxy}" target="_blank" class="btn" style="background: #6366f1; color: white; text-decoration: none; padding: 8px 16px; border-radius: 4px; font-size: 14px;">
              <i class="fa fa-external-link-alt"></i> Open Spark UI
            </a>
            <button onclick="checkSparkJobStatus('${response.job_id}')" class="btn" style="background: #10b981; padding: 8px 16px; border-radius: 4px; font-size: 14px;">
              <i class="fa fa-refresh"></i> Check Status
            </button>
            <button onclick="viewJobLog('${response.job_id}')" class="btn ghost" style="padding: 8px 16px; border-radius: 4px; font-size: 14px;">
              <i class="fa fa-file-text"></i> View Log
            </button>
          </div>
        </div>
        <div style="margin-top: 12px; padding: 10px; background: #fffbeb; border-radius: 6px; border-left: 3px solid #f59e0b;">
          <small style="color: #92400e;">
            <i class="fa fa-info-circle"></i> 
            <strong>Tip:</strong> The Spark UI shows real-time job progress, stages, and task execution details.
          </small>
        </div>
      </div>
    `;
    
    // Auto-open Spark UI in new window if not already open
    if (response.spark_ui_status === 'running') {
      setTimeout(() => {
        window.open(response.spark_ui_proxy, 'SparkUI', 'width=1200,height=800');
      }, 1000);
    }
    
    // Start monitoring job status
    startSparkStatusMonitoring(response.job_id);
    
  } catch (error) {
    resultDiv.innerHTML = `
      <div style="padding: 15px; background: #fee2e2; border-radius: 8px; border: 1px solid #ef4444;">
        <strong style="color: #dc2626;">❌ Error Starting Spark</strong><br>
        <span style="font-size: 14px; color: #6b7280;">${error.message}</span>
      </div>
    `;
    if (statusSpan) statusSpan.innerHTML = '<span style="color: #ef4444;">Error</span>';
  }
  
  btn.disabled = false;
  btn.innerHTML = '<i class="fa fa-play"></i> Run Spark Job';
});

document.getElementById('train-model-btn')?.addEventListener('click', async () => {
  const btn = document.getElementById('train-model-btn');
  const resultDiv = document.getElementById('spark-result');
  const statusSpan = document.getElementById('spark-status');
  
  btn.disabled = true;
  btn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Training...';
  statusSpan.innerHTML = '<span style="color: #f59e0b;">Training...</span>';
  
  try {
    const response = await api('/train', {
      method: 'POST',
      body: JSON.stringify({
        input: 'data/datasets/comprehensive_toxicity_dataset.csv',
        model_out: 'models/spark_lr_model',
        algo: 'logistic',
        max_rows: 10000
      }),
      headers: {'Content-Type': 'application/json'}
    });
    
    if (response.error) {
      throw new Error(response.error);
    }
    
    currentSparkJobId = response.job_id;
    resultDiv.innerHTML = `
      <div style="padding: 15px; background: #dcfce7; border-radius: 8px; border: 1px solid #10b981;">
        <strong style="color: #15803d;">🎓 Model Training Started</strong><br>
        <span style="font-size: 14px; color: #6b7280;">Job ID: ${response.job_id}</span><br>
        <div style="margin-top: 10px;">
          <a href="/spark-proxy/" target="_blank" class="btn" style="background: #6366f1; color: white; text-decoration: none; padding: 8px 16px; border-radius: 4px; font-size: 14px;">
            <i class="fa fa-external-link-alt"></i> Monitor Training
          </a>
          <button onclick="checkSparkJobStatus('${response.job_id}')" class="btn" style="background: #10b981; padding: 8px 16px; border-radius: 4px; font-size: 14px; margin-left: 8px;">
            <i class="fa fa-refresh"></i> Check Progress
          </button>
        </div>
      </div>
    `;
    
    // Start monitoring job status
    startSparkStatusMonitoring(response.job_id);
    
  } catch (error) {
    resultDiv.innerHTML = `
      <div style="padding: 15px; background: #fee2e2; border-radius: 8px; border: 1px solid #ef4444;">
        <strong style="color: #dc2626;">❌ Error Starting Training</strong><br>
        <span style="font-size: 14px; color: #6b7280;">${error.message}</span>
      </div>
    `;
    statusSpan.innerHTML = '<span style="color: #ef4444;">Error</span>';
  }
  
  btn.disabled = false;
  btn.innerHTML = '<i class="fa fa-graduation-cap"></i> Train Model';
});

function startSparkStatusMonitoring(jobId) {
  if (sparkStatusInterval) {
    clearInterval(sparkStatusInterval);
  }
  
  sparkStatusInterval = setInterval(() => {
    checkSparkJobStatus(jobId);
  }, 3000); // Check every 3 seconds
}

async function checkSparkJobStatus(jobId) {
  try {
    const response = await api(`/job-status/${jobId}`);
    const statusSpan = document.getElementById('spark-status');
    
    if (response.error) {
      statusSpan.innerHTML = '<span style="color: #ef4444;">Not Found</span>';
      return;
    }
    
    const status = response.status;
    let statusColor = '#6b7280';
    let statusText = status;
    
    if (status === 'running') {
      statusColor = '#10b981';
      statusText = '🟢 Running';
    } else if (status === 'finished') {
      statusColor = '#3b82f6';
      statusText = '✅ Completed';
      if (sparkStatusInterval) {
        clearInterval(sparkStatusInterval);
        sparkStatusInterval = null;
      }
    } else if (status.startsWith('failed')) {
      statusColor = '#ef4444';
      statusText = '❌ Failed';
      if (sparkStatusInterval) {
        clearInterval(sparkStatusInterval);
        sparkStatusInterval = null;
      }
    }
    
    statusSpan.innerHTML = `<span style="color: ${statusColor};">${statusText}</span>`;
    
  } catch (error) {
    console.error('Error checking job status:', error);
  }
}

