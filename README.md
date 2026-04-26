# Content Automation Demo — Claude Workshop Part 2

A teaching-first content automation app that shows students how APIs chain together. Watch a real-time **Automation X-ray** pipeline as content flows through every stage: scrape → script → image → video → caption → publish.

## What It Does

Paste a URL or describe a content idea. The app automatically:

1. **Scrapes** the URL with FireCrawl (clean markdown, no ads)
2. **Writes** a platform-specific script via OpenRouter LLM
3. **Generates** an AI image with Kie.ai (Nano Banana Pro)
4. **Creates** a short video with Kie.ai (Veo 3.1)
5. **Writes** social media captions
6. **Publishes** to your connected platform via GetLate.dev

Every API call is visible in the live pipeline log so students can see exactly what's happening under the hood.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask 3.x (Python) |
| Database | SQLite (zero-config) |
| Frontend | Jinja2 + Tailwind CSS + Alpine.js (all CDN) |
| Real-time | Server-Sent Events (SSE) — no Redis needed |
| LLM | OpenRouter (multi-model switchboard) |
| Scraping | FireCrawl |
| Image/Video | Kie.ai |
| Publishing | GetLate.dev |
| Deployment | Railway + gunicorn |

## Getting Started

### 1. Clone & install

```bash
git clone https://github.com/jjacuna/content-automation.git
cd content-automation
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Open `.env` and fill in your API keys:

| Key | Where to get it |
|---|---|
| `SECRET_KEY` | Any random string |
| `OPENROUTER_API_KEY` | [openrouter.ai/keys](https://openrouter.ai/keys) |
| `FIRECRAWL_API_KEY` | [firecrawl.dev](https://www.firecrawl.dev/) |
| `KIE_API_KEY` | [kie.ai](https://kie.ai/) |
| `GETLATE_API_KEY` | [getlate.dev](https://getlate.dev/) |

Only `OPENROUTER_API_KEY` is required to start — the other stages fall back to demo placeholders if their key is missing.

### 3. Run

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000).

## Project Structure

```
app.py              # Flask app + routes
pipeline.py         # SSE pipeline orchestrator
models.py           # SQLite models
services/
  openrouter.py     # LLM script generation
  firecrawl.py      # URL scraping
  kie_ai.py         # Image + video generation
  getlate.py        # Publishing
templates/          # Jinja2 HTML templates
static/             # CSS + JS assets
```

## Design

Dark gold theme (`#0B0B0D` background, `#C7A35A` gold accent) matching the CRM Demo from Part 1 of the workshop series.
