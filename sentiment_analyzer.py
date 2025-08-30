from textblob import TextBlob
from typing import Dict

class SentimentAnalyzer:
    def analyze(self, text):
        blob = TextBlob(text)
        pol, subj = blob.sentiment.polarity, blob.sentiment.subjectivity
        return {'polarity' : pol, 'subjectivity' : subj}
    
    