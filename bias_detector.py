from typing import Dict
from configuration import Config

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
    
    