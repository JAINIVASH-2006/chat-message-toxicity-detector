"""
Export and Batch Analysis System
Handles bulk analysis, CSV export, PDF reports
"""
import csv
import io
import json
from datetime import datetime
from enhanced_toxicity_analysis import EnhancedToxicityAnalyzer


class ExportSystem:
    def __init__(self):
        self.analyzer = EnhancedToxicityAnalyzer()
    
    def analyze_batch(self, messages):
        """Analyze multiple messages at once"""
        results = []
        
        for i, msg in enumerate(messages):
            text = msg.get('text', '') or msg.get('message', '') or str(msg)
            
            analysis = self.analyzer.analyze_text(text)
            
            results.append({
                'index': i + 1,
                'text': text[:100] + '...' if len(text) > 100 else text,
                'full_text': text,
                'toxicity_score': analysis['toxicity_score'],
                'toxicity_level': analysis['toxicity_level'],
                'top_category': analysis.get('top_category', 'none'),
                'total_matches': analysis['total_matches'],
                'toxicity_density': analysis['toxicity_density'],
                'categories': analysis['categories'],
                'detected_words': analysis.get('detected_words', [])
            })
        
        return results
    
    def export_to_csv(self, results):
        """Export analysis results to CSV format"""
        output = io.StringIO()
        
        if not results:
            return output.getvalue()
        
        # Define CSV headers
        headers = [
            'Index',
            'Text Preview',
            'Toxicity Score',
            'Risk Level',
            'Top Category',
            'Toxic Words Count',
            'Toxicity Density %',
            'Detected Words'
        ]
        
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        
        for result in results:
            writer.writerow({
                'Index': result['index'],
                'Text Preview': result['text'],
                'Toxicity Score': f"{result['toxicity_score']:.2f}",
                'Risk Level': result['toxicity_level'],
                'Top Category': result['top_category'],
                'Toxic Words Count': result['total_matches'],
                'Toxicity Density %': f"{result['toxicity_density']:.2f}",
                'Detected Words': ', '.join(result['detected_words'][:5])
            })
        
        return output.getvalue()
    
    def export_to_json(self, results):
        """Export analysis results to JSON format"""
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'total_analyzed': len(results),
            'summary': self.generate_summary(results),
            'results': results
        }
        
        return json.dumps(export_data, indent=2)
    
    def generate_summary(self, results):
        """Generate statistical summary of batch analysis"""
        if not results:
            return {}
        
        scores = [r['toxicity_score'] for r in results]
        toxic_count = sum(1 for s in scores if s > 30)
        
        level_counts = {}
        category_counts = {}
        
        for result in results:
            level = result['toxicity_level']
            level_counts[level] = level_counts.get(level, 0) + 1
            
            top_cat = result['top_category']
            if top_cat != 'none':
                category_counts[top_cat] = category_counts.get(top_cat, 0) + 1
        
        return {
            'total_messages': len(results),
            'toxic_messages': toxic_count,
            'safe_messages': len(results) - toxic_count,
            'toxic_percentage': round((toxic_count / len(results)) * 100, 2),
            'average_score': round(sum(scores) / len(scores), 2),
            'max_score': max(scores),
            'min_score': min(scores),
            'level_distribution': level_counts,
            'top_categories': category_counts
        }
    
    def generate_html_report(self, results):
        """Generate a formatted HTML report"""
        summary = self.generate_summary(results)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Toxicity Analysis Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 1200px;
                    margin: 40px auto;
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                }}
                .summary {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .stat-box {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .stat-value {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #667eea;
                }}
                .stat-label {{
                    color: #666;
                    font-size: 14px;
                    margin-top: 5px;
                }}
                .results-table {{
                    background: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                th {{
                    background: #667eea;
                    color: white;
                    padding: 12px;
                    text-align: left;
                }}
                td {{
                    padding: 12px;
                    border-bottom: 1px solid #eee;
                }}
                tr:hover {{
                    background: #f9f9f9;
                }}
                .level-badge {{
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                .level-safe {{ background: #10b981; color: white; }}
                .level-low {{ background: #84cc16; color: white; }}
                .level-medium {{ background: #f59e0b; color: white; }}
                .level-high {{ background: #f97316; color: white; }}
                .level-severe {{ background: #ef4444; color: white; }}
                .level-extreme {{ background: #dc2626; color: white; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Toxicity Analysis Report</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="summary">
                <div class="stat-box">
                    <div class="stat-value">{summary['total_messages']}</div>
                    <div class="stat-label">Total Messages</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{summary['average_score']:.1f}</div>
                    <div class="stat-label">Average Score</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{summary['toxic_percentage']:.1f}%</div>
                    <div class="stat-label">Toxic Rate</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{summary['safe_messages']}</div>
                    <div class="stat-label">Safe Messages</div>
                </div>
            </div>
            
            <div class="results-table">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Text Preview</th>
                            <th>Score</th>
                            <th>Level</th>
                            <th>Category</th>
                            <th>Matches</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for result in results[:100]:  # Limit to first 100 for HTML size
            level_class = f"level-{result['toxicity_level'].lower()}"
            html += f"""
                <tr>
                    <td>{result['index']}</td>
                    <td>{result['text']}</td>
                    <td>{result['toxicity_score']:.1f}</td>
                    <td><span class="level-badge {level_class}">{result['toxicity_level']}</span></td>
                    <td>{result['top_category']}</td>
                    <td>{result['total_matches']}</td>
                </tr>
            """
        
        html += """
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        
        return html


# Global instance
export_system = ExportSystem()
