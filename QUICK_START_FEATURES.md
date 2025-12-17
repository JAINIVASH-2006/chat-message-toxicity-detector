# 🚀 QUICK START GUIDE - Enhanced Toxicity Detection System

## Getting Started (5 Minutes)

### 1. Start the Server
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run the Flask app
python app.py
```

The server will start at **http://localhost:5000**

---

## 🎯 Feature Walkthroughs

### Feature 1: Basic Toxicity Analysis
**Page:** http://localhost:5000/

1. **Enter a message** in the text box
2. Click **"Analyze Message"** 
3. View results:
   - Toxicity Score (0-100)
   - Risk Level (SAFE/LOW/MEDIUM/HIGH/SEVERE/EXTREME)
   - Matched toxic words
   - Category breakdown
   - Severity metrics

**Try these test messages:**
```
✅ Safe: "Hello, how are you today?"
⚠️ Medium: "This is stupid and annoying"
🚨 High: "You're an idiot, I hate you"
```

---

### Feature 2: AI-Powered Suggestions
**Page:** http://localhost:5000/

1. **Enter a toxic message**
2. Click **"Get AI Suggestions"** button
3. View:
   - **Rephrased options** (click to use)
   - Alternative approaches
   - Communication tips
   - Recommended action

**Example:**
```
Original: "You're so stupid!"

Suggestions:
→ "I think there might be a misunderstanding here."
→ "Could you clarify your perspective?"
→ "I respectfully disagree with that point."
```

---

### Feature 3: Real-Time Chat Analysis
**Page:** http://localhost:5000/chat-analyzer

1. **Type messages** in the input box
2. Press **Enter** or click **Send**
3. Watch statistics update in real-time:
   - Overall risk score
   - Message counts by risk level
   - Detected keywords
   - Top categories

4. **Export Report**: Click "Export Report" for JSON file

**Interactive Features:**
- Messages color-coded by toxicity
- Live statistics panel
- Keyword cloud
- Category breakdown

---

### Feature 4: Live Dashboard
**Page:** http://localhost:5000/live-dashboard

**What you'll see:**
- 📊 **6 Animated Metric Cards**
  - Total messages
  - Toxic message count
  - Average toxicity score
  - Community health
  - Toxicity trend (↑↓→)
  - Active users

- 📈 **4 Interactive Charts**
  - Timeline chart (last hour)
  - Risk distribution pie chart
  - Top categories bar chart
  - 24-hour heatmap

- 📰 **Live Activity Feed**
  - Real-time toxic messages stream
  - Color-coded by severity
  - Auto-scrolling

**Note:** Dashboard uses simulated data for demo. In production, it would show real user activity.

---

## 🔧 API Usage Examples

### 1. Analyze Text with Suggestions
```bash
curl -X POST http://localhost:5000/api/suggest-alternatives \
  -H "Content-Type: application/json" \
  -d '{"text": "You are stupid"}'
```

### 2. Get User Profile
```bash
curl http://localhost:5000/api/user-profile/user_123
```

### 3. Moderate Message (with user tracking)
```bash
curl -X POST http://localhost:5000/api/chat/moderate \
  -H "Content-Type: application/json" \
  -d '{"text": "You idiot!", "user": "john_doe"}'
```

### 4. Analyze Conversation
```bash
curl -X POST http://localhost:5000/api/analyze-conversation \
  -H "Content-Type: application/json" \
  -d '{"messages": ["Hello", "You are wrong", "Shut up idiot"]}'
```

### 5. Get Community Stats
```bash
curl http://localhost:5000/api/community-stats
```

---

## 📊 Understanding the Results

### Toxicity Scores
```
0-15:   SAFE     - Clean, respectful message
15-40:  LOW      - Minor issues, mostly safe
40-60:  MEDIUM   - Concerning content
60-80:  HIGH     - Clearly toxic, action needed
80-90:  SEVERE   - Very toxic, block recommended
90-100: EXTREME  - Extremely toxic, immediate action
```

### Risk Levels (User Profiles)
```
Low (0-30):     Normal user behavior
Medium (30-50): Some concerning patterns
High (50-70):   Frequent violations
Severe (70+):   Immediate intervention needed
```

### Recommended Actions
```
LOG_MESSAGE          - Just record for analytics
FLAG_FOR_REVIEW      - Human moderator review
ISSUE_WARNING        - Send warning to user
BLOCK_MESSAGE        - Don't allow message through
TEMPORARY_MUTE       - Mute user for period
REQUIRE_MODERATION   - Pre-approve future messages
SUSPEND_USER         - Temporary account suspension
NOTIFY_ADMIN         - Alert administrators
```

---

## 🎮 Interactive Demo Scenarios

### Scenario 1: Escalating User
**Goal:** See how user tracking works

1. Go to Chat Analyzer
2. Send messages as "user1":
   ```
   Message 1: "Hello everyone"
   Message 2: "This is annoying"
   Message 3: "You're all idiots"
   Message 4: "I hate this place"
   Message 5: "Shut up losers"
   ```

3. Open browser console and check profile:
   ```javascript
   fetch('/api/user-profile/user1').then(r => r.json()).then(console.log)
   ```

4. You'll see:
   - Risk score increasing
   - Violations tracked
   - Patterns detected ("escalating_behavior")
   - Warnings issued
   - Recommended actions escalating

---

### Scenario 2: Conversation Analysis
**Goal:** Analyze entire conversation thread

```python
import requests

messages = [
    "Hey team, what do you think?",
    "I disagree with that approach",
    "You're completely wrong",
    "Stop being so stupid",
    "I hate working with you idiots"
]

response = requests.post(
    'http://localhost:5000/api/analyze-conversation',
    json={'messages': messages}
)

print(response.json())
# Shows: escalation_points, health score, intervention_needed
```

---

### Scenario 3: Suggestion System
**Goal:** Get constructive alternatives

1. Enter: "You're so dumb, this idea is trash"
2. Click "Get AI Suggestions"
3. Get rephrasing options like:
   - "I have concerns about this approach"
   - "Could we explore alternative solutions?"
   - "I think there might be better options"

4. Click any suggestion to replace original text

---

## 🔍 Testing the Features

### Test Messages by Category

**Profanity:**
```
"This is so damn stupid"
"What the hell are you doing?"
```

**Insults:**
```
"You're an idiot"
"Such a loser"
```

**Threats:**
```
"I'll destroy you"
"You're going to pay for this"
```

**Hate Speech:**
```
"I hate you and everything you stand for"
```

**Harassment:**
```
"Nobody likes you, just leave"
"You should quit while you're ahead"
```

---

## 📈 Monitoring Community Health

### Check Dashboard Metrics

1. **Visit:** http://localhost:5000/live-dashboard
2. **Watch for:**
   - Community Health dropping below 70
   - Toxicity Trend showing ↑
   - High-risk messages in activity feed
   - Red zones in hourly heatmap

3. **Take Action:**
   - Review flagged messages
   - Check user profiles
   - Issue warnings/mutes
   - Adjust moderation rules

---

## 🛠️ Customization

### Adjust Risk Thresholds
Edit `user_behavior_tracker.py`:
```python
self.risk_thresholds = {
    'low': 30,      # Change these values
    'medium': 50,
    'high': 70,
    'severe': 85
}
```

### Add Custom Categories
Edit `enhanced_toxicity_analysis.py`:
```python
self.category_weights = {
    'threat': 2.0,
    'your_custom_category': 1.5,  # Add here
    # ...
}
```

### Modify Suggestions
Edit `response_suggestions.py`:
```python
self.toxicity_patterns = {
    'your_pattern': {
        'patterns': [r'\byour_regex\b'],
        'replacements': ['better_word'],
        'suggestions': ['Your suggestion here']
    }
}
```

---

## 🐛 Troubleshooting

### Issue: "Module not found"
```powershell
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Database not found"
```powershell
# Check if data/toxicity_words_database.txt exists
# If not, the system will warn but continue with reduced functionality
```

### Issue: "Port already in use"
```python
# In app.py, change port:
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Use different port
```

### Issue: User profiles not saving
```powershell
# Check directory exists
mkdir data\user_profiles

# Check permissions
# Ensure the app has write access to data/ directory
```

---

## 📚 Next Steps

1. ✅ **Try all features** with test messages
2. 📊 **Explore the dashboard** with simulated data
3. 🔧 **Customize thresholds** for your use case
4. 🚀 **Integrate with your app** using the API
5. 📖 **Read INNOVATIVE_FEATURES.md** for deep dive
6. 🎯 **Add more toxicity words** to the database

---

## 💡 Pro Tips

1. **Batch Analysis**: Use conversation analysis API for thread moderation
2. **User Tracking**: Enable tracking to catch repeat offenders automatically
3. **Export Reports**: Use JSON exports for compliance documentation
4. **Custom Keywords**: Add industry-specific terms to toxicity database
5. **API Integration**: Build Discord/Slack bots using these endpoints
6. **Multi-User Testing**: Test with multiple user IDs to see profile differentiation
7. **Webhook Support**: Can be extended to trigger webhooks on high toxicity

---

## 🎓 Learning Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **Chart.js Docs**: https://www.chartjs.org/docs/
- **Toxicity Detection Research**: Search for "toxic comment classification"
- **NLP Basics**: Understanding text analysis fundamentals

---

## 📞 Need Help?

- Check `INNOVATIVE_FEATURES.md` for detailed feature docs
- Review `README.md` for project overview
- Check Flask logs for error messages
- Examine browser console for frontend issues

---

**Happy Moderating! 🛡️**

*Built with Python, Flask, Chart.js, and a commitment to healthier online communities*
