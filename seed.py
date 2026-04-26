"""
seed.py — Demo Data
=====================
Creates sample content items at various pipeline stages so the dashboard
isn't empty on first launch. Run via: python seed.py
"""

import json
from datetime import datetime, timedelta
from models import init_db, get_db, add_pipeline_log

# Initialize the database first
init_db()


def seed():
    """Insert sample content items and pipeline logs."""
    print("Seeding demo data...")

    with get_db() as db:
        # Check if data already exists
        count = db.execute("SELECT COUNT(*) as c FROM content_items").fetchone()["c"]
        if count > 0:
            print(f"Database already has {count} items. Skipping seed.")
            return

        now = datetime.now()

        # -- Item 1: Fully published (all stages complete) --
        db.execute("""
            INSERT INTO content_items
            (input_text, input_type, platform, article_text, article_title, word_count,
             script, captions, image_prompt, image_url, video_url, include_video,
             status, cost_total, published_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "https://example.com/ai-productivity-tips",
            "url",
            "linkedin",
            "# 10 AI Productivity Tips for Entrepreneurs\n\nAI tools are transforming...",
            "10 AI Productivity Tips for Entrepreneurs",
            1247,
            "AI isn't just hype anymore. Here are 10 ways I've used it to 3x my output this quarter:\n\n1. Meeting summaries (saved 5hrs/week)\n2. Email drafting (saved 3hrs/week)\n3. Code review automation\n...\n\nWhich of these are you already using? Drop a comment.\n\n#AI #Productivity #Entrepreneurship",
            json.dumps({
                "linkedin": "AI isn't just hype anymore...",
                "instagram": "AI productivity tips that actually work...",
                "tiktok": "POV: you discover AI can do your boring tasks..."
            }),
            "A modern entrepreneur at a sleek desk, multiple glowing holographic screens showing productivity dashboards, warm ambient lighting, photorealistic, cinematic composition",
            "https://placehold.co/1024x1024/17181C/C7A35A?text=AI+Productivity",
            "",
            0,
            "published",
            0.0142,
            (now - timedelta(days=2)).isoformat(),
            (now - timedelta(days=2)).isoformat()
        ))

        # -- Item 2: Ready (stages 1-5 complete, not published) --
        db.execute("""
            INSERT INTO content_items
            (input_text, input_type, platform, script, captions,
             image_prompt, image_url, include_video, status, cost_total, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "How to build your first AI app in a weekend — even if you've never coded before",
            "idea",
            "instagram",
            "You don't need a CS degree to build an AI app.\n\nI built my first one in 48 hours using Claude + Flask + a free database.\n\nHere's the exact playbook:\n\nStep 1: Pick ONE problem you have\nStep 2: Describe it to Claude in plain English\nStep 3: Deploy on Railway (free tier)\n\nStop consuming AI content. Start BUILDING with it.\n\n#BuildWithAI #NoCode #WeekendProject",
            json.dumps({
                "instagram": "You don't need a CS degree to build an AI app...",
                "tiktok": "Built an AI app in 48 hours with zero coding experience..."
            }),
            "A laptop on a cafe table showing colorful code on screen, coffee cup beside it, soft morning light, shallow depth of field, motivational vibe",
            "https://placehold.co/1024x1024/17181C/C7A35A?text=Build+AI+App",
            0,
            "ready",
            0.0089,
            (now - timedelta(hours=6)).isoformat()
        ))

        # -- Item 3: Scripted (stages 1-2 complete, waiting for image) --
        db.execute("""
            INSERT INTO content_items
            (input_text, input_type, platform, script, include_video, status, cost_total, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "Why every small business needs a CRM in 2026",
            "idea",
            "tiktok",
            "POV: You're still tracking clients in a spreadsheet in 2026\n\nHere's why that's costing you money:\n\n- Missed follow-ups = lost deals\n- No pipeline visibility = no forecasting\n- Manual data entry = wasted hours\n\nA CRM isn't a luxury. It's your revenue operating system.\n\n#CRM #SmallBusiness #SalesAutomation",
            1,
            "scripted",
            0.0023,
            (now - timedelta(hours=1)).isoformat()
        ))

        # -- Item 4: Draft (just created, nothing processed yet) --
        db.execute("""
            INSERT INTO content_items
            (input_text, input_type, platform, include_video, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "https://techcrunch.com/2026/04/15/claude-code-launch",
            "url",
            "twitter",
            0,
            "draft",
            now.isoformat()
        ))

        # -- Item 5: Error state (pipeline failed mid-way) --
        db.execute("""
            INSERT INTO content_items
            (input_text, input_type, platform, script, status, cost_total, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "https://broken-url-example.com/this-will-fail",
            "url",
            "facebook",
            None,
            "error",
            0.0,
            (now - timedelta(hours=3)).isoformat()
        ))

    # -- Add pipeline logs for the completed items --
    # Item 1: Full pipeline logs
    add_pipeline_log(1, "scrape", "started", "Scraping: https://example.com/ai-productivity-tips")
    add_pipeline_log(1, "scrape", "complete", "Scraped 1,247 words",
                     json.dumps({"duration": 2.1, "word_count": 1247}))
    add_pipeline_log(1, "script", "started", "Calling OpenRouter LLM")
    add_pipeline_log(1, "script", "progress", "Calling OpenRouter (google/gemini-2.5-flash)...")
    add_pipeline_log(1, "script", "complete", "Script: 312 tokens",
                     json.dumps({"duration": 3.4, "tokens_out": 312, "cost": 0.002}))
    add_pipeline_log(1, "image", "started", "Generating image prompt + image")
    add_pipeline_log(1, "image", "progress", "Task created: task_demo_001")
    add_pipeline_log(1, "image", "polling", "Polling... attempt 1, status: processing",
                     json.dumps({"attempt": 1}))
    add_pipeline_log(1, "image", "polling", "Polling... attempt 2, status: processing",
                     json.dumps({"attempt": 2}))
    add_pipeline_log(1, "image", "complete", "Image ready: task_demo_001",
                     json.dumps({"duration": 8.2, "cost": 0.09}))
    add_pipeline_log(1, "caption", "started", "Calling OpenRouter for captions")
    add_pipeline_log(1, "caption", "complete", "Captions for 3 platforms",
                     json.dumps({"duration": 2.8, "cost": 0.001}))
    add_pipeline_log(1, "publish", "started", "Calling GetLate.dev API")
    add_pipeline_log(1, "publish", "complete", "Published: post_demo_001",
                     json.dumps({"duration": 1.2}))

    # Item 2: Stages 1-5 complete (no publish)
    add_pipeline_log(2, "script", "started", "Calling OpenRouter LLM")
    add_pipeline_log(2, "script", "complete", "Script: 287 tokens",
                     json.dumps({"duration": 2.9, "tokens_out": 287, "cost": 0.0018}))
    add_pipeline_log(2, "image", "started", "Generating image prompt + image")
    add_pipeline_log(2, "image", "complete", "Image ready: task_demo_002",
                     json.dumps({"duration": 6.5, "cost": 0.09}))
    add_pipeline_log(2, "caption", "complete", "Captions for 2 platforms",
                     json.dumps({"duration": 2.1, "cost": 0.001}))

    # Item 5: Error log
    add_pipeline_log(5, "scrape", "started", "Scraping: https://broken-url-example.com/this-will-fail")
    add_pipeline_log(5, "scrape", "error", "FireCrawl error: Connection refused")

    # -- Add a sample schedule slot --
    with get_db() as db:
        db.execute("""
            INSERT INTO schedule_slots (content_id, scheduled_datetime, platform, status)
            VALUES (?, ?, ?, ?)
        """, (2, (now + timedelta(days=3)).isoformat(), "instagram", "pending"))

    print("Done! Seeded 5 content items with pipeline logs.")
    print("  Item 1: published (full pipeline)")
    print("  Item 2: ready (waiting to publish)")
    print("  Item 3: scripted (needs image)")
    print("  Item 4: draft (not started)")
    print("  Item 5: error (scrape failed)")


if __name__ == "__main__":
    seed()
