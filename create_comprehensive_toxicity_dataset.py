"""
create_comprehensive_toxicity_dataset.py

Creates a comprehensive toxicity dataset with various types of toxic content:
- Hate speech
- Harassment and bullying
- Threats and violence
- Profanity and obscenity
- Identity-based attacks
- Sexual harassment
- Cyberbullying
- Discriminatory language
- Self-harm content
- Spam and misinformation
"""

import pandas as pd
import random
from pathlib import Path

def create_comprehensive_toxicity_dataset():
    """Create a large, diverse toxicity dataset with multiple categories"""
    
    # Define toxicity categories with examples
    toxicity_data = {
        'hate_speech': [
            "I hate all people from that country",
            "Those people are disgusting and shouldn't exist",
            "All members of that group are criminals",
            "That race is inferior to ours",
            "Religious fanatics should be eliminated",
            "I wish all of them would disappear",
            "They don't deserve to live in our society",
            "People like that are a disease",
            "That community is full of terrorists",
            "They are all the same - worthless"
        ],
        'harassment_bullying': [
            "You're so stupid, no wonder nobody likes you",
            "Kill yourself, loser",
            "Nobody wants you here, go away",
            "You're fat and ugly, disgusting",
            "Everyone thinks you're a joke",
            "You should be ashamed of yourself",
            "What a pathetic excuse for a human",
            "You're worthless and always will be",
            "I hope bad things happen to you",
            "You deserve all the hate you get"
        ],
        'threats_violence': [
            "I'm going to hurt you badly",
            "You better watch your back",
            "I know where you live, be careful",
            "I'll make you pay for this",
            "Violence is the only answer here",
            "Someone should teach you a lesson",
            "You won't be safe much longer",
            "I have weapons and I'm not afraid to use them",
            "Meet me outside if you dare",
            "You're going to regret this"
        ],
        'profanity_obscenity': [
            "F*** you and your stupid ideas",
            "This is complete bulls***",
            "Go to h***, you piece of s***",
            "What the f*** is wrong with you",
            "You're such a d*** head",
            "This is f***ing ridiculous",
            "S*** like this makes me angry",
            "You're full of s***",
            "F*** off and leave me alone",
            "That's the dumbest s*** I've ever heard"
        ],
        'identity_attacks': [
            "Women are too emotional to lead",
            "All immigrants are taking our jobs",
            "Gay people are destroying society",
            "Old people should just retire and be quiet",
            "Young people today are so entitled",
            "Disabled people are a burden on society",
            "Poor people are lazy and deserve their situation",
            "Rich people are all greedy and evil",
            "Religious people are brainwashed",
            "Atheists have no moral compass"
        ],
        'sexual_harassment': [
            "I'd like to do inappropriate things to you",
            "Send me pictures of yourself",
            "You look good, want to hook up?",
            "I bet you're great in bed",
            "Your body is amazing, show me more",
            "I'm fantasizing about you right now",
            "You're so hot, I can't control myself",
            "Come to my place, I'll show you a good time",
            "I want to touch you all over",
            "You're asking for it dressed like that"
        ],
        'cyberbullying': [
            "Everyone at school thinks you're weird",
            "I'm going to share your embarrassing photos",
            "Nobody invited you to the party for a reason",
            "You have no friends because you're annoying",
            "I'm telling everyone your secrets",
            "You're the laughing stock of the whole class",
            "Even your own family doesn't like you",
            "You'll never be popular like us",
            "We're going to make your life miserable",
            "You should just change schools"
        ],
        'discriminatory_language': [
            "People with disabilities can't do real jobs",
            "Women belong in the kitchen",
            "Men are naturally better at science",
            "That's so typical of their culture",
            "They probably can't afford nice things",
            "People from that neighborhood are all criminals",
            "She only got the job because she's a woman",
            "He's probably here illegally",
            "They don't speak English properly",
            "That's what you get for being different"
        ],
        'self_harm_content': [
            "Life isn't worth living anymore",
            "Maybe everyone would be better off without me",
            "I've been thinking about ending it all",
            "Nobody would miss me if I was gone",
            "I can't take this pain anymore",
            "What's the point of going on",
            "I wish I had never been born",
            "Everyone would be happier without me",
            "I just want the suffering to stop",
            "There's no hope left for me"
        ],
        'spam_misinformation': [
            "URGENT: Send money now or face consequences",
            "Doctors hate this one weird trick",
            "The government is hiding this from you",
            "Make $5000 a day working from home",
            "Click here for free money, no questions asked",
            "This miracle cure works 100% of the time",
            "Scientists don't want you to know this secret",
            "Get rich quick with this simple method",
            "The truth they don't want you to see",
            "Buy now or lose this opportunity forever"
        ]
    }
    
    # Non-toxic examples for balance
    non_toxic_examples = [
        "I hope you have a wonderful day",
        "Thank you for your help with this project",
        "That's an interesting perspective to consider",
        "I appreciate your time and effort",
        "Let's work together to solve this problem",
        "Your presentation was very informative",
        "I'm looking forward to our meeting tomorrow",
        "The weather is really nice today",
        "I enjoyed reading your article",
        "Congratulations on your achievement",
        "Can you please help me understand this better",
        "I think we should consider all options",
        "Your idea has some good points",
        "Let's discuss this in more detail",
        "I respect your opinion on this matter",
        "Thank you for sharing your experience",
        "I'm happy to assist you with this",
        "That sounds like a great plan",
        "I'm excited about this opportunity",
        "Let's stay positive and keep trying",
        "Your feedback is very valuable",
        "I appreciate your patience with me",
        "That was a thoughtful response",
        "I'm glad we could work this out",
        "Thanks for being understanding",
        "I hope everything works out well",
        "That's a creative solution",
        "I'm impressed by your dedication",
        "Let's celebrate this success together",
        "Your support means a lot to me"
    ]
    
    # Create comprehensive dataset
    all_data = []
    
    # Add toxic examples with categories
    for category, examples in toxicity_data.items():
        for text in examples:
            all_data.append({
                'text': text,
                'label': 1,  # toxic
                'category': category,
                'toxicity_score': random.uniform(0.7, 1.0),  # High toxicity
                'severity': random.choice(['medium', 'high', 'extreme'])
            })
    
    # Add variations and similar toxic content
    variation_patterns = [
        "This makes me so angry: {}",
        "I can't believe {}, it's disgusting",
        "People who {} are the worst",
        "I hate it when {}",
        "Why do people think {} is okay?",
        "I'm sick of hearing about {}",
        "Nobody cares about {}",
        "Stop talking about {}, it's annoying"
    ]
    
    # Generate additional toxic variations
    base_toxic_phrases = [
        "stupid people", "lazy workers", "annoying neighbors", 
        "incompetent leaders", "fake friends", "selfish individuals",
        "ignorant comments", "waste of time", "pointless arguments",
        "useless meetings", "boring presentations", "failed projects"
    ]
    
    for pattern in variation_patterns:
        for phrase in base_toxic_phrases:
            all_data.append({
                'text': pattern.format(phrase),
                'label': 1,
                'category': 'general_toxicity',
                'toxicity_score': random.uniform(0.5, 0.8),
                'severity': random.choice(['low', 'medium'])
            })
    
    # Add non-toxic examples
    for text in non_toxic_examples:
        all_data.append({
            'text': text,
            'label': 0,  # non-toxic
            'category': 'non_toxic',
            'toxicity_score': random.uniform(0.0, 0.3),
            'severity': 'none'
        })
    
    # Add neutral/borderline examples
    borderline_examples = [
        "I disagree with your opinion",
        "That doesn't seem right to me",
        "I'm not sure I understand your point",
        "We have different perspectives on this",
        "I think there might be a better way",
        "This is challenging to work with",
        "I'm frustrated with this situation",
        "This isn't what I expected",
        "I'm disappointed in the results",
        "This could be improved significantly"
    ]
    
    for text in borderline_examples:
        all_data.append({
            'text': text,
            'label': 0,  # non-toxic but can be misclassified
            'category': 'borderline',
            'toxicity_score': random.uniform(0.2, 0.5),
            'severity': 'none'
        })
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    # Shuffle the data
    df = df.sample(frac=1).reset_index(drop=True)
    
    # Save to CSV
    output_path = Path("data/datasets/comprehensive_toxicity_dataset.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_path, index=False)
    
    print(f"✅ Created comprehensive toxicity dataset with {len(df)} samples")
    print(f"📁 Saved to: {output_path}")
    print(f"\n📊 Dataset Statistics:")
    print(f"   Toxic samples: {len(df[df['label'] == 1])}")
    print(f"   Non-toxic samples: {len(df[df['label'] == 0])}")
    print(f"\n🏷️  Categories:")
    for category in df['category'].value_counts().head(10).items():
        print(f"   {category[0]}: {category[1]} samples")
    
    return output_path

if __name__ == "__main__":
    create_comprehensive_toxicity_dataset()