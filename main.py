import sys, os, json, threading, time
from datetime import datetime
import schedule
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from configuration import Config
from news_collector import NewsCollector  
from sentiment_analyzer import SentimentAnalyzer
from bias_detector import BiasDetector
from web.app import create_app
from typing import Dict
import pandas as pd
class BiasDetector:
    def __init__(self, cfg):
        self.cfg = cfg
    
    def detect_bias(self, article: Dict):
        text = f"{article['title']} {article['description']}"
        score = 0.0
        for k, words in self.cfg.BIAS_KEYWORDS.items():
            hits = sum(w in text for w in words)
            mult = 1.5 if k in ('inflammatory', 'clickbait') else 1
            score += hits * mult
        
        return min(score, 10)

from textblob import TextBlob
from typing import Dict

class SentimentAnalyzer:
    def analyze(self, text):
        blob = TextBlob(text)
        pol, subj = blob.sentiment.polarity, blob.sentiment.subjectivity
        return {'polarity' : pol, 'subjectivity' : subj}
    

import requests, itertools, time
from datetime import datetime
from typing import List, Dict
from configuration import Config

class NewsCollector:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.endpoints = [
            self._from_newsapi,
            self._from_newsdata,
            self._from_thenewsapi
        ]
    # -------------- public --------------
    def collect_latest_news(self):
        articles = []
        try:
            for ep in self.endpoints:
                articles.extend(ep())
        except Exception as e:
            print(f"{ep.__name__} failed, error: {e}")
        
        seen, deduped = set(), []

        for art in articles:
            if art['url'] not in seen:
                seen.add(art['url'])
                deduped.append(art)
        return deduped
    # -------------- private --------------
    def _from_newsapi(self):
        
        url = "https://newsapi.org/v2/everything"
        params = {
            "apiKey" : self.cfg.NEWSAPI_KEY,
            'q' : "affirmative action",
            'language' : 'en',
            'page' : 1,
        }
        response = requests.get(url, params=params)
        data = response.json()
        if data.get('status') != 'ok':
            print("APINEWS Error:", data.get('message', 'Unknown error'))
            return []
        return self._transform(data['articles'])
        
    def _from_newsdata(self):
        url = "https://newsdata.io/api/1/latest"
        params = {
            'apikey': self.cfg.NEWSDATA_KEY,
            'q': 'affirmative action',
            'language': 'en',
            'page': 0,
        }
        articles = []
        while True:
            resp_raw = requests.get(url, params=params)
            try:
                resp = resp_raw.json()
            except ValueError:
                print('Non-JSON Response:', resp_raw.text)
                break
            
            if not isinstance(resp, dict):
                print("Unexpected response type:", type(resp), resp)
                return []
                break

            results = resp.get('results', [])
            articles.extend(results)

            next_page = resp.get('nextPage')
            if not next_page:
                break
            params['page'] = next_page
        return self._transform(articles)
    

    
    def _from_thenewsapi(self):
         url = "https://api.thenewsapi.com/v1/news/all"
         params = {
            "api_token": self.cfg.THENEWSAPI_KEY,
            "search": "affirmative action",
            "language": "en",
            "limit": self.cfg.MAX_ARTICLES_PER_REQUEST,
        }
         resp = requests.get(url, params=params)
         data = resp.json()
         results = data.get('data', [])
         if not isinstance(results, list):
             print('API return not a list', results)
             return []
         return self._transform(results)
    
         
    
    def _transform(self, raw):
        def clean(r):
            return {
                'source' : r.get('source', {}).get("name") or r.get('source_id'),
                'title' : r.get('title', ''),
                'description' : r.get('description', ''),
                'url' : r.get('url'),
                'published_at' : r.get('publishedAt') or r.get('pubDate'),
                'fetched_at' : datetime.now().isoformat()
            }
        return [clean(x) for x in raw if x.get('url')]

class NarrativeDetector:
    def __init__(self):
        self.config = Config()
        self.news_collector = NewsCollector(self.config)
        self.sentiment_analyzer = SentimentAnalyzer()
        self.bias_detector = BiasDetector(self.config)
        self.is_running = False

    def initialize(self):
         print("🚀 Initializing Narrative Manipulation Detector...")
         os.makedirs('data', exist_ok=True)
         os.makedirs('static/img', exist_ok= True)

         if not os.path.exists(self.config.DATA_FILE):
             with open(self.config.DATA_FILE, 'w') as f:
                 json.dump([], f)
         print("✅ System initialized successfully!")
    
    def start_monitoring(self):
        print(">>> Entered start_monitoring")
        print("REGISTERING monitor_cycle IS:", self.monitor_cycle)
        print("UPDATE_INTERVAL IS:", self.config.UPDATE_INTERVAL, type(self.config.UPDATE_INTERVAL))
        job = schedule.every(self.config.UPDATE_INTERVAL).seconds.do(self.monitor_cycle)
        print("JOB REGISTRATION RES:", job)
        schedule.every(self.config.BACKUP_INTERVAL).seconds.do(self._backup)
        print("📡 Scheduled monitoring started...")
        while True:
            schedule.run_pending()
            print(">>> schedule.run_pending() tick")
            time.sleep(1)


    
    #def monitor_cycle(self):
                #print(f"Start monitoring cycle at {datetime.now()}")
                #articles = self.news_collector.collect_latest_news()
                #print(f"Collected {len(articles)} news articles")

                #analyzed_articles = []

                #for article in articles:
                 #   analysis = self.analyze_article(article)
                  #  analyzed_articles.append(analysis)

                #self._save_articles(analyzed_articles)
                
                #all_titles = [a['title'] for a in analyzed_articles]
                #manipulation_scores = self._manipulation_score_advanced(all_titles)

                #for idx, article in enumerate(analyzed_articles):
                  #  orig_score = article['analysis']['manipulation_score']
                   # outlier_score = manipulation_scores[idx] > self.config.MANIPULATION_THRESHOLD
    def monitor_cycle(self):
        print(f"Start monitoring cycle at {datetime.now()}")
        articles = self.news_collector.collect_latest_news()
        print(f"Collected {len(articles)} news articles")

        analyzed_articles = []
        for article in articles:
            analysis = self.analyze_article(article)
            analyzed_articles.append(analysis)

        # 保存分析结果
        self._save_articles(analyzed_articles)

        # 用高级分数算法批量计算
        all_titles = [a['title'] for a in analyzed_articles]
        manipulation_scores = self._manipulation_score_advanced(all_titles)

        # 用新的分数覆盖分析结果
        for idx, article in enumerate(analyzed_articles):
            # 更新 manipulation_score 字段（覆盖旧分数）
            article['analysis']['manipulation_score'] = manipulation_scores[idx]

            # 更新高操纵性flag
            article['analysis']['is_high_manipulation'] = manipulation_scores[idx] > self.config.MANIPULATION_THRESHOLD

        # 如果你想再次保存覆盖，可以再保存一次
        self._save_articles(analyzed_articles)

                    

    
    def analyze_article(self, article):
        title = article.get('title') or ''
        description = article.get('description') or ''
        sentiment = self.sentiment_analyzer.analyze(title + ' ' + description)

        bias_score = self.bias_detector.detect_bias(article)

        manipulation_score = self._calculate_manipulation_score(sentiment, bias_score, article)

        article['analysis'] = {
            'sentiment' : sentiment,
            'bias_score' : bias_score,
            'manipulation_score' :manipulation_score,
            'analyzed_at' : datetime.now().isoformat(),
            'is_high_manipulation' : manipulation_score > self.config.MANIPULATION_THRESHOLD
        }

        return article
    
    def _calculate_manipulation_score(self, sentiment, bias_score, article):
        score = 0

        if abs(sentiment['polarity']) >= 0.7:
            score += 2

        if sentiment['subjectivity'] >= 0.8:
            score += 1.5

        score += bias_score

        title_lower = article['title'].lower()
        clickbait_words = [
    "shocking", "unbelievable", "you won’t believe", "exposed", "secret",
    "top", "the truth about", "never seen before", "revealed", "surprising",
    "this is what happens", "will blow your mind", "can‘t believe", "must see",
    "what happened next", "goes viral", "insane", "the reason why", "miracle",
    "will change your life", "hidden", "uncovered", "no one tells you", "jaw-dropping",
    "one simple trick", "instantly", "this is why", "epic", "game changer"
]

        for word in clickbait_words:
            if word in title_lower:
                score += 1
        
        return min(score, 10)
    
    def _manipulation_score_advanced(self, all_titles):
        if not all_titles or all(not t.strip() for t in all_titles):
            print("Warning: all_titles is empty or contains only empty/stop words. manipulation_score_advanced skipped.")
            return [0.0] * len(all_titles)
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        vectorizer = TfidfVectorizer()
        tfdif = vectorizer.fit_transform(all_titles)
        sim_matrix = cosine_similarity(tfdif)
        sim_to_others = sim_matrix.mean(axis = 1)
        manipulation_score = 1 - sim_to_others
        return manipulation_score
            

    def _save_articles(self, articles):
        #Load the existing data
        try:
            with open(self.config.DATA_FILE, 'r') as f:
                existing_articles = json.load(f)
            
            #Build a quick look-up set for uniqueness and screen new data for uniqueness
            existing_url = {article['url'] for article in existing_articles}
            new_articles = [a for a in articles if a['url'] not in existing_url]

            #Merge the data, cap the number
            all_articles = (existing_articles + new_articles) [-1000:]

            #Save (overwrite) the combined data back to disk
            with open(self.config.DATA_FILE, 'w') as f:
                json.dump(all_articles, f)

            print(f"Saved {len(new_articles)} new articles")
        except Exception as e:
            print(f"Error saving articles: {str(e)}")

    def _backup(self):
        df = pd.read_json(self.config.DATA_FILE)
        stamp = datetime.now().strftime("%Y%m%d%H%M")
        df.to_csv(f"data/backup_{stamp}.csv", index = False)

    def run_web_interface(self):
        """Start the web interface"""
        app = create_app(self.config)
        print(f"🌐 Starting web interface at http://{self.config.FLASK_HOST}:{self.config.FLASK_PORT}")
        app.run(host=self.config.FLASK_HOST, 
               port=self.config.FLASK_PORT, 
               debug=self.config.FLASK_DEBUG)
        
def main():
    detector = NarrativeDetector()

    try:
        detector.initialize()

        detector.start_monitoring()
        
    except KeyboardInterrupt:
            print("\nShutting down...")
            detector.is_running = False
    except Exception as e:
            print(f"Fatal error: {str(e)}")
            sys.exit(1)

if __name__ == '__main__':
    main()





            

            



        


