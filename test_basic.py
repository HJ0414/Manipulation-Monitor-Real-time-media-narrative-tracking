def test_sentiment():
    from sentiment_analyzer import SentimentAnalyzer
    s = SentimentAnalyzer().analyze("Great Success")
    assert -1.0<=s['polarity'] <= 1.0

def test_bias():
    from bias_detector import BiasDetector
    from configuration import Config
    dummy = {"title": "Shocking truth revealed", "description": ""}
    assert BiasDetector(Config()).detect_bias(dummy) > 0