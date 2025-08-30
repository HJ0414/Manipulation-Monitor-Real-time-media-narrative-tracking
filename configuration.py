import os
from dotenv import load_dotenv

load_dotenv()
class Config:
    NEWSAPI_KEY = os.getenv('NEWSAPI_KEY', 'affirmative action')
    NEWSDATA_KEY = os.getenv('NEWSDATA_KEY', 'affirmative action')
    THENEWSAPI_KEY = os.getenv('THENEWSAPI_KEY', 'affirmative action')

    NEWS_SOURCES = [
        'bbc-news', 'cnn', 'fox-news', 'reuters', 'associated-press',
        'the-new-york-times', 'the-washington-post', 'usa-today',
        'breitbart-news', 'the-huffington-post', 'politico'
    ]

    CATEGORIES = ['politics', 'technology', 'business', 'health', 'science']

    MANIPULATION_THRESHOLD = 6.5
    UPDATE_INTERVAL = 300
    MAX_ARTICLES_PER_REQUEST = 100

    DATA_FILE = 'data/articles.json' 
    BACKUP_INTERVAL = 3600

    FLASK_DEBUG = False 
    FLASK_HOST = '127.0.0.1'
    FLASK_PORT = 5000
    
    BIAS_KEYWORDS = {
        'left': ['progressive', 'liberal', 'democrat', 'socialism', 'climate change'],
        'right': ['conservative', 'republican', 'traditional', 'free market', 'patriot'],
        'inflammatory': ['shocking', 'outrageous', 'scandal', 'exposed', 'devastating'],
        'clickbait': ['you won\'t believe', 'shocking truth', 'experts hate', 'one weird trick', "shocking", "unbelievable", "you won’t believe", "exposed", "secret",
    "top", "the truth about", "never seen before", "revealed", "surprising",
    "this is what happens", "will blow your mind", "can’t believe", "must see",
    "what happened next", "goes viral", "insane", "the reason why", "miracle",
    "will change your life", "hidden", "uncovered", "no one tells you", "jaw-dropping",
    "one simple trick", "instantly", "this is why", "epic", "game changer"]
    }

def test_config():
    config = Config()
    print("✅ Configuration loaded successfully!")
    print(f"📰 Monitoring {len(config.NEWS_SOURCES)} news sources")
    print(f"🔍 Tracking {len(config.CATEGORIES)} categories")
    print(f"⚡ Update interval: {config.UPDATE_INTERVAL} seconds")
    return True

if __name__ == "__main__":
    test_config()