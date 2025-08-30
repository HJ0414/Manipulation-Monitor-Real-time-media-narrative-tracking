Narrative Evolution Tracker
===========================

Lightweight Flask app to collect news, analyze sentiment/bias, and build story timelines by URL or title‑similarity clustering. Ships with a simple API and a realtime dashboard to visualize headline evolution.

Features
--------
- Collects articles from multiple APIs (keys optional for demo)
- Analyzes sentiment (TextBlob) and a simple bias score
- Builds evolution timelines:
  - by URL (same URL = same story)
  - by title similarity (TF‑IDF + DBSCAN clustering)
- REST API: parse and fetch stories
- Dashboard: bar chart that updates periodically

Quick Start
-----------

1) Environment & dependencies
```
python3 -m venv .venv
source .venv/bin/activate
pip install -U flask textblob requests python-dotenv scikit-learn pandas
python -m textblob.download_corpora
```

2) Optional API keys (.env or shell)
```
NEWSAPI_KEY=...
NEWSDATA_KEY=...
THENEWSAPI_KEY=...
```

3) Run the app
```
python -c "from web.app import create_app; from configuration import Config; create_app(Config()).run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=False)"
```

Open `http://127.0.0.1:5000`

API
---
- GET `/api/stories`
  - Returns the contents of `data/articles.json`
- POST `/api/parse`
  - Fetch + analyze + persist new snapshots
  - Query params:
    - `mode=title` → cluster by title similarity and assign `topic_cluster`
    - default (no param) → group by URL

Dashboard
---------
- Page: `/` (template in `template/dashboard.html`)
- Script: `static/js/realtime_chart.js` (polls `/api/stories` every minute)
- “Trigger Parse” button calls `POST /api/parse`

Data
----
- Stored at `data/articles.json`
- Article fields (common):
  - `source`, `title`, `description`, `url`, `published_at`, `fetched_at`
  - `analysis`: `{ sentiment: { polarity, subjectivity }, bias_score, manipulation_score }`
  - `evolution_index`: integer within a story/cluster (0 = earliest)
  - `topic_cluster`: integer label when `mode=title`

Project Layout
--------------
- `web/app.py` — Flask app factory (registers blueprints)
- `web/blueprints_api.py` — `/api/stories`, `/api/parse`
- `web/blueprints_dashboard.py` — `/` HTML dashboard
- `news_collector.py` — fetches articles from APIs
- `sentiment_analyzer.py` — TextBlob sentiment
- `bias_detector.py` — simple keyword bias score
- `evolution_tracker.py` — URL timeline and title‑similarity clustering
- `static/` — JS and assets; `template/` — Jinja templates

Troubleshooting
---------------
- Port already in use (5000):
  - Find & kill: `lsof -nP -iTCP:5000 -sTCP:LISTEN` → `kill -9 <PID>`
  - Or run another port: change `port=5001` in the run command
- “Access denied” / debugger screen:
  - Debug is off by default; if cached, try incognito or different browser
- No data on chart:
  - Click “Trigger Parse” or `curl -X POST http://127.0.0.1:5000/api/parse`
  - For title clustering: `curl -X POST "http://127.0.0.1:5000/api/parse?mode=title"`

Notes
-----
- This is a minimal research/demo tool, not production‑grade. API responses and clustering quality depend on available keys and incoming data.

