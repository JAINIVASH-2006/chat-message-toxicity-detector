"""
Enhanced Toxicity Analysis Module
Uses comprehensive 2000+ word toxicity database with severity levels
"""

import os
import re
from typing import Dict, List, Tuple
from collections import defaultdict

class EnhancedToxicityAnalyzer:
    def __init__(self, database_path='data/toxicity_words_database.txt'):
        """Initialize the analyzer with toxicity database"""
        self.toxicity_db = {}
        self.category_weights = {
            'threat': 2.0,
            'severe_toxic': 1.8,
            'violence': 1.7,
            'identity_hate': 1.6,
            'sexual': 1.4,
            'profanity': 1.2,
            'obscene': 1.3,
            'insult': 1.0,
            'toxic': 1.1
        }
        self.load_database(database_path)
        
    def load_database(self, database_path):
        """Load toxicity words from database file"""
        full_path = os.path.join(os.path.dirname(__file__), database_path)
        
        if not os.path.exists(full_path):
            print(f"Warning: Toxicity database not found at {full_path}")
            return
            
        with open(full_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                    
                try:
                    parts = line.split('|')
                    if len(parts) == 3:
                        word, severity, category = parts
                        self.toxicity_db[word.lower()] = {
                            'severity': int(severity),
                            'category': category
                        }
                except Exception as e:
                    print(f"Error parsing line: {line} - {e}")
                    
        print(f"Loaded {len(self.toxicity_db)} toxicity words from database")
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze text for toxicity with detailed scoring
        
        Returns:
            dict with toxicity_score, toxicity_level, matched_words, 
            category_breakdown, severity_breakdown
        """
        if not text:
            return self._empty_result()
            
        # Normalize text
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        # Find matches
        matches = []
        category_scores = defaultdict(float)
        severity_counts = defaultdict(int)
        
        for word in words:
            if word in self.toxicity_db:
                word_info = self.toxicity_db[word]
                severity = word_info['severity']
                category = word_info['category']
                
                matches.append({
                    'word': word,
                    'severity': severity,
                    'category': category
                })
                
                # Calculate weighted score for this word
                base_score = severity / 5.0  # Normalize to 0-1
                category_weight = self.category_weights.get(category, 1.0)
                weighted_score = base_score * category_weight
                
                category_scores[category] += weighted_score
                severity_counts[severity] += 1
        
        # Calculate overall toxicity score
        if not matches:
            return self._empty_result()
            
        # Total toxicity calculation
        total_score = sum(m['severity'] for m in matches)
        max_severity = max(m['severity'] for m in matches)
        avg_severity = total_score / len(matches)
        
        # Weighted toxicity score (0-100)
        toxicity_score = min(100, (
            (avg_severity / 5.0) * 40 +  # Average severity contributes 40%
            (max_severity / 5.0) * 30 +   # Max severity contributes 30%
            (len(matches) / len(words)) * 30  # Density contributes 30%
        ) * 100)
        
        # Determine toxicity level
        toxicity_level = self._get_toxicity_level(toxicity_score, max_severity)
        
        # Sort matches by severity
        matches.sort(key=lambda x: x['severity'], reverse=True)
        
        # Get top category
        top_category = max(category_scores.items(), key=lambda x: x[1])[0] if category_scores else 'none'
        
        return {
            'toxicity_score': round(toxicity_score, 2),
            'toxicity_level': toxicity_level,
            'matched_words': matches[:10],  # Top 10 matches
            'total_matches': len(matches),
            'category_breakdown': dict(category_scores),
            'severity_breakdown': dict(severity_counts),
            'top_category': top_category,
            'max_severity': max_severity,
            'avg_severity': round(avg_severity, 2),
            'toxicity_density': round((len(matches) / len(words)) * 100, 2),
            'warning_message': self._get_warning_message(toxicity_level, top_category)
        }
    
    def _empty_result(self) -> Dict:
        """Return empty result for non-toxic text"""
        return {
            'toxicity_score': 0,
            'toxicity_level': 'SAFE',
            'matched_words': [],
            'total_matches': 0,
            'category_breakdown': {},
            'severity_breakdown': {},
            'top_category': 'none',
            'max_severity': 0,
            'avg_severity': 0,
            'toxicity_density': 0,
            'warning_message': 'This message appears to be safe and non-toxic.'
        }
    
    def _get_toxicity_level(self, score: float, max_severity: int) -> str:
        """Determine toxicity level based on score and severity"""
        if max_severity >= 5:
            return 'EXTREME'
        elif max_severity >= 4:
            return 'SEVERE'
        elif score >= 70:
            return 'HIGH'
        elif score >= 40:
            return 'MEDIUM'
        elif score >= 15:
            return 'LOW'
        else:
            return 'SAFE'
    
    def _get_warning_message(self, level: str, category: str) -> str:
        """Get warning message based on toxicity level"""
        messages = {
            'EXTREME': f'⚠️ EXTREME TOXICITY DETECTED - Contains {category} content that may violate terms of service.',
            'SEVERE': f'⚠️ SEVERE TOXICITY - High level of {category} content detected.',
            'HIGH': f'⚠️ HIGH TOXICITY - Significant {category} content present.',
            'MEDIUM': f'⚠️ MODERATE TOXICITY - Some {category} content detected.',
            'LOW': f'⚠️ LOW TOXICITY - Minor {category} content present.',
            'SAFE': '✅ This message appears to be safe and respectful.'
        }
        return messages.get(level, 'Message analyzed.')
    
    def batch_analyze(self, texts: List[str]) -> List[Dict]:
        """Analyze multiple texts"""
        return [self.analyze_text(text) for text in texts]
    
    def get_statistics(self) -> Dict:
        """Get statistics about the toxicity database"""
        severity_dist = defaultdict(int)
        category_dist = defaultdict(int)
        
        for word_info in self.toxicity_db.values():
            severity_dist[word_info['severity']] += 1
            category_dist[word_info['category']] += 1
        
        return {
            'total_words': len(self.toxicity_db),
            'severity_distribution': dict(severity_dist),
            'category_distribution': dict(category_dist),
            'categories': list(self.category_weights.keys())
        }


# Global analyzer instance
_analyzer = None

def get_analyzer():
    """Get or create global analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = EnhancedToxicityAnalyzer()
    return _analyzer

def analyze_text(text: str) -> Dict:
    """Convenience function to analyze text"""
    return get_analyzer().analyze_text(text)

def batch_analyze(texts: List[str]) -> List[Dict]:
    """Convenience function to analyze multiple texts"""
    return get_analyzer().batch_analyze(texts)

def get_statistics() -> Dict:
    """Get database statistics"""
    return get_analyzer().get_statistics()


if __name__ == '__main__':
    # Test the analyzer
    analyzer = EnhancedToxicityAnalyzer()
    
    test_messages = [
        "Hello, how are you today?",
        "You're such an idiot!",
        "I hate you and wish you would die!",
        "This is fucking bullshit!",
        "You're a stupid moron and a loser.",
        "I hope you get cancer and die slowly."
    ]
    
    print("=" * 80)
    print("ENHANCED TOXICITY ANALYZER TEST")
    print("=" * 80)
    print(f"\nDatabase Statistics:")
    stats = analyzer.get_statistics()
    print(f"Total Words: {stats['total_words']}")
    print(f"Categories: {', '.join(stats['categories'])}")
    print(f"\nSeverity Distribution:")
    for sev, count in sorted(stats['severity_distribution'].items()):
        print(f"  Level {sev}: {count} words")
    
    print("\n" + "=" * 80)
    print("TESTING MESSAGES")
    print("=" * 80)
    
    for i, msg in enumerate(test_messages, 1):
        result = analyzer.analyze_text(msg)
        print(f"\n[{i}] Message: \"{msg}\"")
        print(f"    Toxicity Score: {result['toxicity_score']}/100")
        print(f"    Level: {result['toxicity_level']}")
        print(f"    Matches: {result['total_matches']}")
        if result['matched_words']:
            top_words = ', '.join([f"{m['word']}({m['severity']})" for m in result['matched_words'][:5]])
            print(f"    Top Words: {top_words}")
        print(f"    Top Category: {result['top_category']}")
        print(f"    Warning: {result['warning_message']}")
