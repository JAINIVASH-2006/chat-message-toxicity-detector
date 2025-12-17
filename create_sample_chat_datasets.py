"""
Create 30 Sample Chat Message Datasets for Toxicity Analysis
Each dataset represents different scenarios and communication contexts
"""
import pandas as pd
import json
from pathlib import Path
import random

# Create output directory
output_dir = Path('data/sample_datasets')
output_dir.mkdir(parents=True, exist_ok=True)

# Dataset 1: Gaming Chat - Toxic
gaming_toxic = [
    {"message": "You're absolute trash at this game", "timestamp": "2025-11-16 10:15:23", "user": "player1"},
    {"message": "uninstall noob", "timestamp": "2025-11-16 10:16:45", "user": "player2"},
    {"message": "kys you're so bad", "timestamp": "2025-11-16 10:17:12", "user": "player3"},
    {"message": "gg easy, you guys suck", "timestamp": "2025-11-16 10:18:34", "user": "player4"},
    {"message": "worst team ever, idiots", "timestamp": "2025-11-16 10:19:56", "user": "player5"},
]
pd.DataFrame(gaming_toxic).to_csv(output_dir / '01_gaming_toxic.csv', index=False)

# Dataset 2: Gaming Chat - Clean
gaming_clean = [
    {"message": "Good game everyone!", "timestamp": "2025-11-16 11:20:12", "user": "player1"},
    {"message": "Nice play!", "timestamp": "2025-11-16 11:21:34", "user": "player2"},
    {"message": "Let's try again, we can do this", "timestamp": "2025-11-16 11:22:45", "user": "player3"},
    {"message": "Great teamwork", "timestamp": "2025-11-16 11:23:56", "user": "player4"},
    {"message": "Thanks for the match!", "timestamp": "2025-11-16 11:24:23", "user": "player5"},
]
pd.DataFrame(gaming_clean).to_csv(output_dir / '02_gaming_clean.csv', index=False)

# Dataset 3: Social Media Comments - Mixed
social_media = [
    {"message": "This is disgusting, delete this", "timestamp": "2025-11-16 12:10:00", "user": "user1"},
    {"message": "Love your content!", "timestamp": "2025-11-16 12:11:00", "user": "user2"},
    {"message": "You're an idiot for posting this", "timestamp": "2025-11-16 12:12:00", "user": "user3"},
    {"message": "Great perspective, thanks for sharing", "timestamp": "2025-11-16 12:13:00", "user": "user4"},
    {"message": "Nobody cares what you think", "timestamp": "2025-11-16 12:14:00", "user": "user5"},
]
pd.DataFrame(social_media).to_csv(output_dir / '03_social_media_mixed.csv', index=False)

# Dataset 4: Customer Service Chat - Professional
customer_service = [
    {"message": "Hello, I need help with my order", "timestamp": "2025-11-16 13:00:00", "user": "customer1"},
    {"message": "This service is terrible!", "timestamp": "2025-11-16 13:01:00", "user": "customer2"},
    {"message": "Thank you for your assistance", "timestamp": "2025-11-16 13:02:00", "user": "customer3"},
    {"message": "Your company is a scam", "timestamp": "2025-11-16 13:03:00", "user": "customer4"},
    {"message": "I appreciate your quick response", "timestamp": "2025-11-16 13:04:00", "user": "customer5"},
]
pd.DataFrame(customer_service).to_csv(output_dir / '04_customer_service.csv', index=False)

# Dataset 5: Forum Discussion - Hate Speech
hate_speech_forum = [
    {"message": "People like you don't belong here", "timestamp": "2025-11-16 14:00:00", "user": "user1"},
    {"message": "You should be banned for existing", "timestamp": "2025-11-16 14:01:00", "user": "user2"},
    {"message": "Go back to where you came from", "timestamp": "2025-11-16 14:02:00", "user": "user3"},
    {"message": "Your kind makes me sick", "timestamp": "2025-11-16 14:03:00", "user": "user4"},
    {"message": "I hope you suffer", "timestamp": "2025-11-16 14:04:00", "user": "user5"},
]
pd.DataFrame(hate_speech_forum).to_csv(output_dir / '05_hate_speech_forum.csv', index=False)

# Dataset 6: Workplace Slack - Professional
workplace_slack = [
    {"message": "Meeting at 3pm today", "timestamp": "2025-11-16 15:00:00", "user": "manager1"},
    {"message": "I'll have the report ready by EOD", "timestamp": "2025-11-16 15:01:00", "user": "employee1"},
    {"message": "Thanks for your help on the project", "timestamp": "2025-11-16 15:02:00", "user": "employee2"},
    {"message": "Can we schedule a call?", "timestamp": "2025-11-16 15:03:00", "user": "employee3"},
    {"message": "Great work team!", "timestamp": "2025-11-16 15:04:00", "user": "manager2"},
]
pd.DataFrame(workplace_slack).to_csv(output_dir / '06_workplace_professional.csv', index=False)

# Dataset 7: Political Forum - Heated Debate
political_debate = [
    {"message": "Your political views are absolutely stupid", "timestamp": "2025-11-16 16:00:00", "user": "debater1"},
    {"message": "Only an idiot would believe that", "timestamp": "2025-11-16 16:01:00", "user": "debater2"},
    {"message": "I disagree, but I respect your opinion", "timestamp": "2025-11-16 16:02:00", "user": "debater3"},
    {"message": "You're what's wrong with this country", "timestamp": "2025-11-16 16:03:00", "user": "debater4"},
    {"message": "Let's discuss this civilly", "timestamp": "2025-11-16 16:04:00", "user": "moderator1"},
]
pd.DataFrame(political_debate).to_csv(output_dir / '07_political_debate.csv', index=False)

# Dataset 8: Teen Chat - Cyberbullying
cyberbullying = [
    {"message": "Nobody likes you at school", "timestamp": "2025-11-16 17:00:00", "user": "student1"},
    {"message": "You're so ugly and fat", "timestamp": "2025-11-16 17:01:00", "user": "student2"},
    {"message": "Everyone talks about how weird you are", "timestamp": "2025-11-16 17:02:00", "user": "student3"},
    {"message": "Just disappear already", "timestamp": "2025-11-16 17:03:00", "user": "student4"},
    {"message": "You have no friends loser", "timestamp": "2025-11-16 17:04:00", "user": "student5"},
]
pd.DataFrame(cyberbullying).to_csv(output_dir / '08_cyberbullying.csv', index=False)

# Dataset 9: Support Group - Positive
support_group = [
    {"message": "You're not alone in this", "timestamp": "2025-11-16 18:00:00", "user": "member1"},
    {"message": "Thank you for sharing your story", "timestamp": "2025-11-16 18:01:00", "user": "member2"},
    {"message": "We're here for you", "timestamp": "2025-11-16 18:02:00", "user": "member3"},
    {"message": "Stay strong, you've got this", "timestamp": "2025-11-16 18:03:00", "user": "member4"},
    {"message": "Sending positive vibes your way", "timestamp": "2025-11-16 18:04:00", "user": "member5"},
]
pd.DataFrame(support_group).to_csv(output_dir / '09_support_group.csv', index=False)

# Dataset 10: Sports Fan Chat - Aggressive
sports_aggressive = [
    {"message": "Your team is garbage", "timestamp": "2025-11-16 19:00:00", "user": "fan1"},
    {"message": "Worst players I've ever seen", "timestamp": "2025-11-16 19:01:00", "user": "fan2"},
    {"message": "The ref is blind and stupid", "timestamp": "2025-11-16 19:02:00", "user": "fan3"},
    {"message": "You fans are all idiots", "timestamp": "2025-11-16 19:03:00", "user": "fan4"},
    {"message": "This game is rigged!", "timestamp": "2025-11-16 19:04:00", "user": "fan5"},
]
pd.DataFrame(sports_aggressive).to_csv(output_dir / '10_sports_aggressive.csv', index=False)

# Dataset 11-30: Generate more diverse datasets
datasets = [
    ("11_dating_app_harassment", [
        "Hey beautiful, show me more pics",
        "You're too stuck up",
        "Why won't you respond? Bit** ",
        "Nobody would want you anyway",
        "You look desperate"
    ]),
    ("12_product_reviews_angry", [
        "This product is absolute trash",
        "Worst purchase ever, scam!",
        "The company should be ashamed",
        "Don't waste your money on this crap",
        "Total garbage, avoid at all costs"
    ]),
    ("13_news_comments_divisive", [
        "This is fake news propaganda",
        "Mainstream media lies",
        "Anyone who believes this is brainwashed",
        "The truth is being censored",
        "Wake up sheeple"
    ]),
    ("14_reddit_wholesome", [
        "This made my day, thank you!",
        "You're breathtaking!",
        "Faith in humanity restored",
        "Take my upvote kind stranger",
        "This is the wholesome content I needed"
    ]),
    ("15_twitch_stream_chat", [
        "Pog champion!",
        "L streamer",
        "Actually so bad at this game",
        "Best stream ever!",
        "Chat is toxic today"
    ]),
    ("16_discord_server_toxic", [
        "Mods are power tripping losers",
        "This server is dead",
        "Admin abusing their power",
        "Everyone here is cringe",
        "Worst community ever"
    ]),
    ("17_instagram_comments", [
        "Gorgeous! 😍",
        "You're trying too hard",
        "Attention seeker",
        "Looking amazing!",
        "Stop photoshopping everything"
    ]),
    ("18_youtube_comments", [
        "First!",
        "This content is trash",
        "Unsubscribed",
        "Best video ever!",
        "Algorithm brought me here"
    ]),
    ("19_email_spam_aggressive", [
        "CLICK NOW OR LOSE EVERYTHING",
        "You've been selected for $1000000",
        "Urgent: Your account will be closed",
        "Last warning before legal action",
        "Act now or face consequences"
    ]),
    ("20_classroom_online_disruptive", [
        "This class is boring",
        "Teacher doesn't know what they're talking about",
        "Can we end early?",
        "This is a waste of time",
        "Nobody cares about this subject"
    ]),
    ("21_marketplace_negotiations", [
        "Your price is ridiculous",
        "I can get this cheaper elsewhere",
        "You're trying to rip me off",
        "Lowest I'll go is half",
        "This is overpriced junk"
    ]),
    ("22_mental_health_supportive", [
        "It's okay to not be okay",
        "You matter and you're valued",
        "Taking care of your mental health is important",
        "We all struggle sometimes",
        "You're stronger than you think"
    ]),
    ("23_fitness_community_motivational", [
        "You've got this! Keep pushing!",
        "Progress not perfection",
        "Every rep counts",
        "Believe in yourself",
        "Beast mode activated!"
    ]),
    ("24_relationship_advice_constructive", [
        "Communication is key",
        "Consider their perspective too",
        "It's important to set boundaries",
        "Take time for self-reflection",
        "Couples therapy might help"
    ]),
    ("25_tech_support_frustrated", [
        "This software is absolute garbage",
        "Your support team is useless",
        "Worst tech company ever",
        "I want my money back immediately",
        "This doesn't work and you don't care"
    ]),
    ("26_book_club_discussion", [
        "The character development was excellent",
        "I disagree with that interpretation",
        "This book changed my perspective",
        "The plot twist was unexpected",
        "Looking forward to next month's pick"
    ]),
    ("27_cooking_community", [
        "This recipe is amazing!",
        "Looks disgusting honestly",
        "You're not a real chef",
        "Thanks for sharing!",
        "Gordon Ramsay would be ashamed"
    ]),
    ("28_parenting_forum_judgmental", [
        "You're ruining your child",
        "That's not how you parent",
        "Your kids will resent you",
        "Everyone has their own approach",
        "Judge less, support more"
    ]),
    ("29_crypto_trading_panic", [
        "HODL!!! Don't panic sell!",
        "We're all going to lose everything",
        "This is a scam coin",
        "To the moon! 🚀",
        "You're all idiots for investing"
    ]),
    ("30_educational_content_spam", [
        "Check out my channel for more!",
        "Link in bio!",
        "Subscribe to my course!",
        "Join my exclusive group!",
        "Click here for free stuff!"
    ]),
]

for filename, messages in datasets:
    df = pd.DataFrame([
        {"message": msg, "timestamp": f"2025-11-16 {10+i:02d}:00:00", "user": f"user{i+1}"}
        for i, msg in enumerate(messages)
    ])
    df.to_csv(output_dir / f'{filename}.csv', index=False)

# Create catalog file
catalog = {
    "datasets": [
        {"id": "01_gaming_toxic", "name": "Gaming Chat - Toxic", "description": "Toxic gaming chat messages", "category": "gaming", "toxicity": "high", "messages": 5},
        {"id": "02_gaming_clean", "name": "Gaming Chat - Clean", "description": "Positive gaming interactions", "category": "gaming", "toxicity": "low", "messages": 5},
        {"id": "03_social_media_mixed", "name": "Social Media - Mixed", "description": "Mixed toxicity social media comments", "category": "social", "toxicity": "medium", "messages": 5},
        {"id": "04_customer_service", "name": "Customer Service", "description": "Customer service interactions", "category": "business", "toxicity": "medium", "messages": 5},
        {"id": "05_hate_speech_forum", "name": "Hate Speech Forum", "description": "Forum with hate speech content", "category": "forum", "toxicity": "high", "messages": 5},
        {"id": "06_workplace_professional", "name": "Workplace Professional", "description": "Professional workplace chat", "category": "workplace", "toxicity": "low", "messages": 5},
        {"id": "07_political_debate", "name": "Political Debate", "description": "Heated political discussion", "category": "politics", "toxicity": "high", "messages": 5},
        {"id": "08_cyberbullying", "name": "Cyberbullying", "description": "Teen cyberbullying messages", "category": "social", "toxicity": "high", "messages": 5},
        {"id": "09_support_group", "name": "Support Group", "description": "Positive support group chat", "category": "community", "toxicity": "low", "messages": 5},
        {"id": "10_sports_aggressive", "name": "Sports Fan Chat", "description": "Aggressive sports fan comments", "category": "sports", "toxicity": "high", "messages": 5},
        {"id": "11_dating_app_harassment", "name": "Dating App Harassment", "description": "Harassment on dating platforms", "category": "dating", "toxicity": "high", "messages": 5},
        {"id": "12_product_reviews_angry", "name": "Angry Product Reviews", "description": "Aggressive product reviews", "category": "reviews", "toxicity": "high", "messages": 5},
        {"id": "13_news_comments_divisive", "name": "Divisive News Comments", "description": "Polarizing news discussion", "category": "news", "toxicity": "medium", "messages": 5},
        {"id": "14_reddit_wholesome", "name": "Reddit Wholesome", "description": "Positive Reddit community", "category": "social", "toxicity": "low", "messages": 5},
        {"id": "15_twitch_stream_chat", "name": "Twitch Stream Chat", "description": "Live streaming platform chat", "category": "streaming", "toxicity": "medium", "messages": 5},
        {"id": "16_discord_server_toxic", "name": "Discord Toxic Server", "description": "Toxic Discord server chat", "category": "gaming", "toxicity": "high", "messages": 5},
        {"id": "17_instagram_comments", "name": "Instagram Comments", "description": "Social media image comments", "category": "social", "toxicity": "medium", "messages": 5},
        {"id": "18_youtube_comments", "name": "YouTube Comments", "description": "Video platform comments", "category": "video", "toxicity": "medium", "messages": 5},
        {"id": "19_email_spam_aggressive", "name": "Aggressive Email Spam", "description": "Threatening spam emails", "category": "email", "toxicity": "medium", "messages": 5},
        {"id": "20_classroom_online_disruptive", "name": "Disruptive Online Classroom", "description": "Disruptive student messages", "category": "education", "toxicity": "medium", "messages": 5},
        {"id": "21_marketplace_negotiations", "name": "Marketplace Negotiations", "description": "Aggressive marketplace haggling", "category": "commerce", "toxicity": "medium", "messages": 5},
        {"id": "22_mental_health_supportive", "name": "Mental Health Support", "description": "Supportive mental health community", "category": "health", "toxicity": "low", "messages": 5},
        {"id": "23_fitness_community_motivational", "name": "Fitness Motivation", "description": "Motivational fitness community", "category": "fitness", "toxicity": "low", "messages": 5},
        {"id": "24_relationship_advice_constructive", "name": "Relationship Advice", "description": "Constructive relationship guidance", "category": "relationships", "toxicity": "low", "messages": 5},
        {"id": "25_tech_support_frustrated", "name": "Frustrated Tech Support", "description": "Angry tech support interactions", "category": "technology", "toxicity": "high", "messages": 5},
        {"id": "26_book_club_discussion", "name": "Book Club Discussion", "description": "Literary discussion group", "category": "literature", "toxicity": "low", "messages": 5},
        {"id": "27_cooking_community", "name": "Cooking Community", "description": "Mixed cooking forum comments", "category": "food", "toxicity": "medium", "messages": 5},
        {"id": "28_parenting_forum_judgmental", "name": "Judgmental Parenting Forum", "description": "Judgmental parenting discussions", "category": "parenting", "toxicity": "high", "messages": 5},
        {"id": "29_crypto_trading_panic", "name": "Crypto Trading Panic", "description": "Volatile crypto trading chat", "category": "finance", "toxicity": "medium", "messages": 5},
        {"id": "30_educational_content_spam", "name": "Educational Spam", "description": "Promotional educational spam", "category": "education", "toxicity": "low", "messages": 5},
    ]
}

with open(output_dir / 'catalog.json', 'w') as f:
    json.dump(catalog, f, indent=2)

print("✅ Created 30 sample chat datasets")
print(f"📁 Location: {output_dir.absolute()}")
print("📊 Catalog file created: catalog.json")
