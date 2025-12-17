"""
Dataset Generator - Creates 20 sample datasets for comprehensive toxicity analysis
"""
import pandas as pd
import numpy as np
import random
from pathlib import Path
import json
from datetime import datetime, timedelta

# Create sample datasets directory
datasets_dir = Path('data/sample_datasets')
datasets_dir.mkdir(parents=True, exist_ok=True)

# Sample toxic messages (for demonstration - these are mild examples)
TOXIC_SAMPLES = [
    "You're so stupid", "I hate this", "This is garbage", "You're worthless",
    "Shut up idiot", "That's pathetic", "You're a loser", "This sucks badly",
    "You're annoying", "I'm done with you", "This is terrible", "You're wrong",
    "That's dumb", "You're crazy", "This is awful", "You make me sick",
    "I can't stand you", "You're the worst", "This is ridiculous", "You're useless"
]

# Sample clean messages
CLEAN_SAMPLES = [
    "Hello everyone!", "How are you doing today?", "Great job on that project!",
    "Thanks for your help", "I appreciate your effort", "That's a good idea",
    "Nice to meet you", "Have a wonderful day", "Good morning team",
    "Thanks for sharing", "I agree with that", "That makes sense",
    "Well done!", "Keep up the good work", "That's interesting",
    "I understand your point", "Thanks for explaining", "Good question",
    "I'm happy to help", "That sounds reasonable", "Great presentation",
    "I like your approach", "That's very helpful", "Excellent work",
    "I'm excited about this", "That's a smart solution", "Well said",
    "I support that idea", "That's very thoughtful", "Good observation",
    "Thanks for your time", "I learned something new", "That's impressive",
    "Good teamwork", "I'm glad to be here", "That's creative",
    "Well organized", "That's professional", "Good communication",
    "I respect your opinion", "That's constructive feedback", "Good collaboration"
]

# User names for variety
USERNAMES = [
    "alice123", "bob_user", "charlie99", "diana_m", "edward_k", "fiona_x",
    "george_t", "hannah_s", "ivan_p", "julia_w", "kevin_r", "lisa_g",
    "mike_d", "nancy_b", "oscar_l", "paula_n", "quinn_v", "rachel_z",
    "steve_h", "tina_f", "user001", "member_42", "chat_user", "guest_99"
]

# Platform types
PLATFORMS = ["discord", "slack", "teams", "forum", "chat", "social"]

def generate_timestamp(start_date, days_range=30):
    """Generate random timestamp within date range"""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    random_days = random.randint(0, days_range)
    random_hours = random.randint(0, 23)
    random_minutes = random.randint(0, 59)
    
    timestamp = start + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def create_dataset(name, size, toxicity_ratio=0.2, start_date="2024-01-01"):
    """Create a dataset with specified parameters"""
    data = []
    toxic_count = int(size * toxicity_ratio)
    clean_count = size - toxic_count
    
    # Generate toxic messages
    for _ in range(toxic_count):
        message = random.choice(TOXIC_SAMPLES)
        # Add variations
        if random.random() > 0.7:
            message += " " + random.choice(["!!!", "...", "???", "dude", "man"])
        
        data.append({
            'message': message,
            'user': random.choice(USERNAMES),
            'timestamp': generate_timestamp(start_date),
            'platform': random.choice(PLATFORMS),
            'is_toxic': 1,
            'toxicity_score': round(random.uniform(0.6, 1.0), 2),
            'category': random.choice(['insult', 'profanity', 'toxic', 'obscene'])
        })
    
    # Generate clean messages
    for _ in range(clean_count):
        message = random.choice(CLEAN_SAMPLES)
        data.append({
            'message': message,
            'user': random.choice(USERNAMES),
            'timestamp': generate_timestamp(start_date),
            'platform': random.choice(PLATFORMS),
            'is_toxic': 0,
            'toxicity_score': round(random.uniform(0.0, 0.3), 2),
            'category': 'clean'
        })
    
    # Shuffle the data
    random.shuffle(data)
    return pd.DataFrame(data)

# Dataset configurations
DATASETS = [
    {"name": "gaming_chat_1000", "size": 1000, "toxicity_ratio": 0.25, "start_date": "2024-01-01"},
    {"name": "social_media_2000", "size": 2000, "toxicity_ratio": 0.15, "start_date": "2024-01-15"},
    {"name": "discord_server_1500", "size": 1500, "toxicity_ratio": 0.30, "start_date": "2024-02-01"},
    {"name": "forum_discussions_800", "size": 800, "toxicity_ratio": 0.10, "start_date": "2024-02-10"},
    {"name": "team_chat_600", "size": 600, "toxicity_ratio": 0.05, "start_date": "2024-02-20"},
    {"name": "public_comments_3000", "size": 3000, "toxicity_ratio": 0.35, "start_date": "2024-03-01"},
    {"name": "support_tickets_500", "size": 500, "toxicity_ratio": 0.20, "start_date": "2024-03-10"},
    {"name": "community_posts_1200", "size": 1200, "toxicity_ratio": 0.18, "start_date": "2024-03-15"},
    {"name": "live_stream_chat_2500", "size": 2500, "toxicity_ratio": 0.28, "start_date": "2024-04-01"},
    {"name": "customer_feedback_400", "size": 400, "toxicity_ratio": 0.12, "start_date": "2024-04-05"},
    {"name": "review_comments_1800", "size": 1800, "toxicity_ratio": 0.22, "start_date": "2024-04-10"},
    {"name": "slack_workspace_700", "size": 700, "toxicity_ratio": 0.08, "start_date": "2024-04-15"},
    {"name": "reddit_style_2200", "size": 2200, "toxicity_ratio": 0.26, "start_date": "2024-05-01"},
    {"name": "youtube_comments_3500", "size": 3500, "toxicity_ratio": 0.40, "start_date": "2024-05-10"},
    {"name": "corporate_chat_300", "size": 300, "toxicity_ratio": 0.03, "start_date": "2024-05-15"},
    {"name": "gaming_lobby_1600", "size": 1600, "toxicity_ratio": 0.32, "start_date": "2024-06-01"},
    {"name": "educational_forum_900", "size": 900, "toxicity_ratio": 0.07, "start_date": "2024-06-05"},
    {"name": "news_comments_2800", "size": 2800, "toxicity_ratio": 0.33, "start_date": "2024-06-10"},
    {"name": "help_desk_messages_650", "size": 650, "toxicity_ratio": 0.14, "start_date": "2024-06-15"},
    {"name": "mixed_platform_4000", "size": 4000, "toxicity_ratio": 0.24, "start_date": "2024-07-01"}
]

def main():
    print("🔄 Creating 20 Sample Datasets for Toxicity Analysis...")
    print("=" * 60)
    
    dataset_info = []
    total_messages = 0
    
    for config in DATASETS:
        print(f"📊 Creating {config['name']}...")
        
        # Create dataset
        df = create_dataset(
            config['name'], 
            config['size'], 
            config['toxicity_ratio'], 
            config['start_date']
        )
        
        # Save to CSV
        filepath = datasets_dir / f"{config['name']}.csv"
        df.to_csv(filepath, index=False)
        
        # Calculate statistics
        toxic_count = len(df[df['is_toxic'] == 1])
        clean_count = len(df[df['is_toxic'] == 0])
        avg_toxicity = df['toxicity_score'].mean()
        
        dataset_info.append({
            'name': config['name'],
            'filepath': str(filepath),
            'total_messages': config['size'],
            'toxic_messages': toxic_count,
            'clean_messages': clean_count,
            'toxicity_percentage': round((toxic_count / config['size']) * 100, 1),
            'avg_toxicity_score': round(avg_toxicity, 3),
            'date_range': config['start_date'],
            'platforms': list(df['platform'].unique()),
            'categories': list(df['category'].unique())
        })
        
        total_messages += config['size']
        print(f"   ✅ {config['size']:,} messages ({toxic_count} toxic, {clean_count} clean)")
    
    # Save dataset catalog
    catalog = {
        'generated_at': datetime.now().isoformat(),
        'total_datasets': len(DATASETS),
        'total_messages': total_messages,
        'datasets': dataset_info
    }
    
    catalog_path = datasets_dir / 'catalog.json'
    with open(catalog_path, 'w') as f:
        json.dump(catalog, f, indent=2)
    
    print(f"\n✅ Successfully created {len(DATASETS)} datasets!")
    print(f"📈 Total messages: {total_messages:,}")
    print(f"📁 Location: {datasets_dir}")
    print(f"📋 Catalog: {catalog_path}")
    
    # Create summary report
    summary_lines = [
        "# Dataset Collection Summary\n",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        f"Total Datasets: {len(DATASETS)}\n",
        f"Total Messages: {total_messages:,}\n\n",
        "## Dataset Details\n\n"
    ]
    
    for info in dataset_info:
        summary_lines.append(f"### {info['name']}\n")
        summary_lines.append(f"- **Messages:** {info['total_messages']:,}\n")
        summary_lines.append(f"- **Toxic:** {info['toxic_messages']} ({info['toxicity_percentage']}%)\n")
        summary_lines.append(f"- **Clean:** {info['clean_messages']}\n")
        summary_lines.append(f"- **Avg Toxicity:** {info['avg_toxicity_score']}\n")
        summary_lines.append(f"- **Platforms:** {', '.join(info['platforms'])}\n\n")
    
    summary_path = datasets_dir / 'README.md'
    with open(summary_path, 'w') as f:
        f.writelines(summary_lines)
    
    print(f"📄 Summary report: {summary_path}")

if __name__ == "__main__":
    main()