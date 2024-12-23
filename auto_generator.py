import time
import random
from datetime import datetime
import schedule
from app import create_app
from app.models import db, Article
from app.utils import generate_article_with_claude

# Base topics with example scenarios to inspire Claude
TOPIC_TEMPLATES = {
    "Crypto": [
        "Something funny about Bitcoin maximalists",
        "Ridiculous new crypto project",
        "Crypto bros doing crypto things",
        "Web3 gone wrong",
        "NFT collectors being NFT collectors"
    ],
    "Tech CEOs": [
        "Tech CEO does something totally normal but fails",
        "Billionaire's weird new project",
        "Startup founder reality check",
        "Silicon Valley drama"
    ],
    "AI & Robots": [
        "AI does something unexpectedly human",
        "Robot rebellion but it's silly",
        "ChatGPT misunderstandings",
        "AI tries to understand humans"
    ],
    "Aliens & Conspiracy": [
        "Aliens react to human technology",
        "Conspiracy theory but it's mundane",
        "Secret society doing ordinary things",
        "Government cover-up of something ridiculous"
    ],
    "Finance": [
        "Wall Street but it's actually Main Street",
        "Traders discovering basic life facts",
        "Market manipulation but it's absurd",
        "Traditional finance vs crypto chaos"
    ],
    "Tech Culture": [
        "Developers touching grass",
        "Startup culture gone wrong",
        "Tech workers discovering real world",
        "Silicon Valley vs Reality"
    ]
}

def generate_random_article():
    print(f"\n[{datetime.now()}] Starting article generation...")
    
    try:
        app = create_app()
        with app.app_context():
            # Pick random category and template
            category = random.choice(list(TOPIC_TEMPLATES.keys()))
            template = random.choice(TOPIC_TEMPLATES[category])
            
            print(f"Selected category: {category}")
            print(f"Template: {template}")
            
            # Let Claude be creative with the template
            result = generate_article_with_claude(
                topic=template,
                style="satirical",
                tone="humorous"
            )
            
            if result['success']:
                print(f"Successfully generated article: {result['title']}")
                delay = random.randint(10, 120)
                print(f"Next article scheduled in {delay} minutes")
            else:
                print(f"Error generating article: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"Error in generate_random_article: {str(e)}")

def run_generator():
    print("Starting automatic article generator...")
    
    while True:
        try:
            # Generate first article immediately
            generate_random_article()
            
            # Random delay between 10-120 minutes
            delay = random.randint(10, 120)
            print(f"Waiting {delay} minutes until next article...")
            time.sleep(delay * 60)  # Convert minutes to seconds
            
        except KeyboardInterrupt:
            print("\nStopping article generator...")
            break
        except Exception as e:
            print(f"Error in run_generator: {str(e)}")
            # Wait 5 minutes before retrying on error
            time.sleep(300)

if __name__ == "__main__":
    run_generator() 