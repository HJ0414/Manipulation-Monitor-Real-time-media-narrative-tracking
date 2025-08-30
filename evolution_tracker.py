from collections import defaultdict
from datetime import datetime, timezone
import hashlib, re, json, os
from typing import List, Dict

class EvolutionTracker:
    def __init__(self, data_file = 'data/articles.json'):
        self.path = data_file
    
    @staticmethod
    def _fingerprint(url):
        slug = re.sub(r"https?://", "", url).split('?')[0]
        return hashlib.md5(slug.encode()).hexdigest()
    

    def build_timeline(self):
        with open(self.path) as f:
            articles = json.load(f)
        buckets = defaultdict(list)
        for art in articles:
            buckets[self._fingerprint(art['url'])].append(art)
        
        for fp, chain in buckets.items():
            chain.sort(key = lambda x:x['published_at'] or x['fetched_at'])

            for i, art in enumerate(chain):
                art['evolution_index'] = i
            
        with open(self.path, 'w') as f:
            json.dump(articles, f, indent = 2)
    
    def build_timeline_by_title_similarity(self, eps: float = 0.6, min_samples: int = 1):
        """Group articles by title similarity using TF-IDF + DBSCAN (cosine).
        Assign an evolution_index within each cluster ordered by time.
        """
        with open(self.path) as f:
            articles: List[Dict] = json.load(f)

        if not articles:
            return

        titles = [(a.get('title') or '').strip() for a in articles]
        # Vectorize titles
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.cluster import DBSCAN
        import numpy as np

        vectorizer = TfidfVectorizer(stop_words='english')
        X = vectorizer.fit_transform(titles)

        # Cluster with cosine distance
        clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
        labels = clustering.fit_predict(X)

        # Group by label (-1 treated as its own cluster)
        label_to_indices: Dict[int, List[int]] = defaultdict(list)
        for idx, lab in enumerate(labels):
            label_to_indices[int(lab)].append(idx)

        # For each cluster, order by time and assign evolution_index
        def parse_time(a: Dict):
            return (a.get('published_at') or a.get('fetched_at') or '')

        for lab, idxs in label_to_indices.items():
            idxs_sorted = sorted(idxs, key=lambda i: parse_time(articles[i]))
            for order, art_idx in enumerate(idxs_sorted):
                articles[art_idx]['evolution_index'] = order
                articles[art_idx]['topic_cluster'] = int(lab)

        with open(self.path, 'w') as f:
            json.dump(articles, f, indent=2)