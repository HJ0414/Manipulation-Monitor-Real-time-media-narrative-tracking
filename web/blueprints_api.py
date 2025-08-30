from flask import Blueprint, jsonify
import json, os

api_bp = Blueprint("api", __name__)

@api_bp.route("/stories")
def stories():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "articles.json")
    if not os.path.exists(path):
        # fallback to project root data path
        path = os.path.join(os.getcwd(), "data", "articles.json")
    with open(path) as f:
        data = json.load(f)
    return jsonify(data)

@api_bp.route("/parse", methods=["POST"])
def parse_now():
    """Trigger a one-off collection + analysis and return latest data."""
    try:
        from configuration import Config
        from news_collector import NewsCollector
        from sentiment_analyzer import SentimentAnalyzer
        from bias_detector import BiasDetector
        from datetime import datetime

        cfg = Config()
        collector = NewsCollector(cfg)
        analyzer = SentimentAnalyzer()
        bias = BiasDetector(cfg)

        articles = collector.collect_latest_news()
        analyzed = []
        for a in articles:
            sentiment = analyzer.analyze((a.get('title') or '') + ' ' + (a.get('description') or ''))
            bias_score = bias.detect_bias(a)
            a['analysis'] = {
                'sentiment': sentiment,
                'bias_score': bias_score,
                'manipulation_score': bias_score,  # simple baseline
                'analyzed_at': datetime.now().isoformat()
            }
            analyzed.append(a)

        # save
        data_path = os.path.join(os.getcwd(), "data", "articles.json")
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        try:
            with open(data_path, 'r') as f:
                existing = json.load(f)
        except Exception:
            existing = []

        # allow multiple snapshots per URL if content changed
        url_to_last = {}
        for x in existing:
            url_to_last[x.get('url')] = x

        appended = 0
        for a in analyzed:
            u = a.get('url')
            if not u:
                continue
            prev = url_to_last.get(u)
            if prev is None:
                existing.append(a)
                url_to_last[u] = a
                appended += 1
            else:
                if (a.get('title') != prev.get('title') or
                    a.get('description') != prev.get('description') or
                    a.get('published_at') != prev.get('published_at')):
                    existing.append(a)
                    url_to_last[u] = a
                    appended += 1

        with open(data_path, 'w') as f:
            json.dump(existing, f)

        # build evolution timeline (assign evolution_index)
        try:
            from flask import request
            from evolution_tracker import EvolutionTracker
            mode = (request.args.get('mode') or '').lower()
            tracker = EvolutionTracker(data_file=data_path)
            if mode == 'title':
                tracker.build_timeline_by_title_similarity()
            else:
                tracker.build_timeline()
        except Exception as _e:
            pass

        return jsonify({"added": appended, "total": len(existing)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
