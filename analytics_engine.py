"""
Advanced Analytics Engine for Toxicity Trends
Tracks historical data and generates insights
"""
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


class AnalyticsEngine:
    def __init__(self, data_file='data/analytics_history.json'):
        self.data_file = data_file
        self.history = self.load_history()
    
    def load_history(self):
        """Load historical data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading history: {e}")
        return {
            'messages': [],
            'daily_stats': {},
            'category_trends': defaultdict(list)
        }
    
    def save_history(self):
        """Save historical data to file"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def log_analysis(self, text, analysis_result):
        """Log a new analysis to history"""
        timestamp = datetime.now().isoformat()
        date_key = datetime.now().strftime('%Y-%m-%d')
        
        entry = {
            'timestamp': timestamp,
            'date': date_key,
            'text_length': len(text),
            'toxicity_score': analysis_result.get('toxicity_score', 0),
            'level': analysis_result.get('toxicity_level', 'SAFE'),
            'categories': analysis_result.get('categories', {}),
            'total_matches': analysis_result.get('total_matches', 0)
        }
        
        # Add to messages
        self.history['messages'].append(entry)
        
        # Keep only last 1000 messages to prevent file bloat
        if len(self.history['messages']) > 1000:
            self.history['messages'] = self.history['messages'][-1000:]
        
        # Update daily stats
        if date_key not in self.history['daily_stats']:
            self.history['daily_stats'][date_key] = {
                'count': 0,
                'total_score': 0,
                'toxic_count': 0,
                'safe_count': 0
            }
        
        stats = self.history['daily_stats'][date_key]
        stats['count'] += 1
        stats['total_score'] += entry['toxicity_score']
        
        if entry['toxicity_score'] > 30:
            stats['toxic_count'] += 1
        else:
            stats['safe_count'] += 1
        
        self.save_history()
    
    def get_trends(self, days=7):
        """Get toxicity trends over the last N days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        trends = []
        current_date = start_date
        
        while current_date <= end_date:
            date_key = current_date.strftime('%Y-%m-%d')
            stats = self.history['daily_stats'].get(date_key, {
                'count': 0,
                'total_score': 0,
                'toxic_count': 0,
                'safe_count': 0
            })
            
            avg_score = stats['total_score'] / stats['count'] if stats['count'] > 0 else 0
            
            trends.append({
                'date': date_key,
                'count': stats['count'],
                'avg_toxicity': round(avg_score, 2),
                'toxic_count': stats['toxic_count'],
                'safe_count': stats['safe_count']
            })
            
            current_date += timedelta(days=1)
        
        return trends
    
    def get_category_distribution(self, days=7):
        """Get distribution of toxicity categories"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        category_counts = defaultdict(int)
        
        for msg in self.history['messages']:
            msg_date = datetime.fromisoformat(msg['timestamp'])
            if start_date <= msg_date <= end_date:
                categories = msg.get('categories', {})
                for cat, score in categories.items():
                    if score > 0:
                        category_counts[cat] += 1
        
        return dict(category_counts)
    
    def get_peak_hours(self):
        """Identify peak hours for toxic content"""
        hour_counts = defaultdict(lambda: {'total': 0, 'toxic': 0})
        
        for msg in self.history['messages']:
            try:
                hour = datetime.fromisoformat(msg['timestamp']).hour
                hour_counts[hour]['total'] += 1
                if msg['toxicity_score'] > 30:
                    hour_counts[hour]['toxic'] += 1
            except:
                continue
        
        return dict(hour_counts)
    
    def get_statistics(self):
        """Get overall statistics"""
        if not self.history['messages']:
            return {
                'total_analyzed': 0,
                'avg_toxicity': 0,
                'median_toxicity': 0,
                'toxic_percentage': 0,
                'most_common_level': 'SAFE'
            }
        
        scores = [msg['toxicity_score'] for msg in self.history['messages']]
        toxic_count = sum(1 for s in scores if s > 30)
        
        level_counts = defaultdict(int)
        for msg in self.history['messages']:
            level_counts[msg['level']] += 1
        
        most_common_level = max(level_counts.items(), key=lambda x: x[1])[0]
        
        return {
            'total_analyzed': len(scores),
            'avg_toxicity': round(statistics.mean(scores), 2),
            'median_toxicity': round(statistics.median(scores), 2),
            'toxic_percentage': round((toxic_count / len(scores)) * 100, 2),
            'most_common_level': most_common_level,
            'level_distribution': dict(level_counts)
        }
    
    def get_improvement_score(self):
        """Calculate improvement trend (positive = improving)"""
        if len(self.history['messages']) < 10:
            return 0
        
        # Compare first half vs second half
        mid = len(self.history['messages']) // 2
        first_half = self.history['messages'][:mid]
        second_half = self.history['messages'][mid:]
        
        first_avg = statistics.mean([m['toxicity_score'] for m in first_half])
        second_avg = statistics.mean([m['toxicity_score'] for m in second_half])
        
        # Lower score in second half = improvement (positive value)
        improvement = first_avg - second_avg
        
        return round(improvement, 2)
    
    def get_insights(self):
        """Generate AI-like insights from data"""
        stats = self.get_statistics()
        trends = self.get_trends(days=7)
        improvement = self.get_improvement_score()
        
        insights = []
        
        # Toxicity level insight
        if stats['avg_toxicity'] < 20:
            insights.append({
                'type': 'positive',
                'title': 'Healthy Communication',
                'message': f"Average toxicity is only {stats['avg_toxicity']}/100. Great job maintaining respectful conversations!"
            })
        elif stats['avg_toxicity'] > 50:
            insights.append({
                'type': 'warning',
                'title': 'High Toxicity Detected',
                'message': f"Average toxicity is {stats['avg_toxicity']}/100. Consider implementing stricter moderation."
            })
        
        # Trend insight
        if improvement > 5:
            insights.append({
                'type': 'positive',
                'title': 'Improving Trend',
                'message': f"Toxicity has decreased by {improvement} points. Your community is becoming more positive!"
            })
        elif improvement < -5:
            insights.append({
                'type': 'warning',
                'title': 'Worsening Trend',
                'message': f"Toxicity has increased by {abs(improvement)} points. Time to take action."
            })
        
        # Volume insight
        if stats['total_analyzed'] > 100:
            insights.append({
                'type': 'info',
                'title': 'Active Monitoring',
                'message': f"Analyzed {stats['total_analyzed']} messages. You're actively protecting your community."
            })
        
        # Percentage insight
        if stats['toxic_percentage'] < 10:
            insights.append({
                'type': 'positive',
                'title': 'Low Toxicity Rate',
                'message': f"Only {stats['toxic_percentage']}% of messages are toxic. Excellent community culture!"
            })
        
        return insights


# Global instance
analytics = AnalyticsEngine()
