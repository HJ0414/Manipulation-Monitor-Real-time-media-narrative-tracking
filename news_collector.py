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
        resp = requests.get(url, params=params)
        data = resp.json()
        if data.get('status') != 'ok':
            print("APINEWS Error:", data.get('message', 'Unknown error'))
            return []
        return self._transform(data.get("articles", []))
    def _from_newsdata(self):
        url = "https://newsdata.io/api/1/latest"
        params = {
            'apikey' : self.cfg.NEWSDATA_KEY,
            'q' : 'affirmative action',
            'language' : 'en',
            'page' : 0,
        }
        articles = []
        while True:
            resp_raw = requests.get(url, params=params)
            try:
                resp = resp_raw.json()
            except ValueError:
                print('Non-JSON Response:', resp_raw.text)
                break
            results = resp.get('results', []) if isinstance(resp, dict) else []
            articles.extend(results)
            next_page = resp.get('nextPage') if isinstance(resp, dict) else None
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
         results = data.get('data', []) if isinstance(data, dict) else []
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
