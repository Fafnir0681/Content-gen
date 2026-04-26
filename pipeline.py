"""
pipeline.py — Pipeline Orchestrator
======================================
This is the CORE of the app. It runs the 6-stage content automation pipeline
and emits SSE events at every step so the "Automation X-ray" can visualize it.

Pipeline stages:
  1. scrape   — FireCrawl (skip if input_type='idea')
  2. script   — OpenRouter LLM generates post text
  3. image    — Kie.ai Nano Banana Pro generates image
  4. video    — Kie.ai Veo 3.1 generates video (optional)
  5. caption  — OpenRouter LLM generates platform-specific captions
  6. publish  — GetLate.dev posts to social media (only when explicitly triggered)

Each stage:
  - Updates the content_item status in the database
  - Logs to pipeline_logs
  - Emits SSE events via the emit_event callback
  - Tracks duration and cost
"""

import json
import time
from datetime import datetime

from models import get_content_item, update_content_item, add_pipeline_log
from services.firecrawl import scrape_url
from services.openrouter import generate_script, generate_image_prompt, generate_captions
from services.kie_ai import generate_image, generate_video
from services.getlate import publish_post


# ---------------------------------------------------------------------------
# run_pipeline() — Execute stages 1-5 (everything except publish)
# ---------------------------------------------------------------------------
def run_pipeline(content_id, emit_event):
    """
    Run the full content pipeline for a content item.
    Executes stages 1-5 sequentially, emitting SSE events at each step.

    Stage 6 (publish) is NOT run here — it's triggered separately via /api/publish/<id>.

    Args:
        content_id: ID of the content_item to process
        emit_event: Callback function(stage, status, message, detail=None)
    """
    # Load the content item
    item = get_content_item(content_id)
    if not item:
        emit_event("pipeline", "error", f"Content item {content_id} not found")
        return

    total_cost = 0.0
    pipeline_start = time.time()

    emit_event("pipeline", "started",
               f"Kicking off your content machine! We'll turn your {'link' if item['input_type'] == 'url' else 'idea'} into a ready-to-post piece of content.",
               {"content_id": content_id, "input_type": item["input_type"]})

    # Update status to processing
    update_content_item(content_id, status="processing")

    try:
        # ==================================================================
        # STAGE 1: SCRAPE — Fetch article from URL (skip if 'idea')
        # ==================================================================
        cost = stage_scrape(content_id, item, emit_event)
        total_cost += cost
        # Reload item to get updated fields
        item = get_content_item(content_id)

        # ==================================================================
        # STAGE 2: SCRIPT — Generate social media post text
        # ==================================================================
        cost = stage_script(content_id, item, emit_event)
        total_cost += cost
        item = get_content_item(content_id)

        # ==================================================================
        # STAGE 3: IMAGE — Generate image with Kie.ai
        # ==================================================================
        cost = stage_image(content_id, item, emit_event)
        total_cost += cost
        item = get_content_item(content_id)

        # ==================================================================
        # STAGE 4: VIDEO — Generate video (optional)
        # ==================================================================
        cost = stage_video(content_id, item, emit_event)
        total_cost += cost
        item = get_content_item(content_id)

        # ==================================================================
        # STAGE 5: CAPTION — Generate platform-specific captions
        # ==================================================================
        cost = stage_caption(content_id, item, emit_event)
        total_cost += cost

        # ==================================================================
        # PIPELINE COMPLETE
        # ==================================================================
        total_duration = round(time.time() - pipeline_start, 1)
        update_content_item(content_id, status="ready", cost_total=total_cost)

        emit_event("pipeline", "complete",
                   f"All done! Your content is ready to post. The whole thing took {total_duration}s and cost ${total_cost:.4f}. That's the power of automation — what would take you an hour, the machine did in under a minute.",
                   {"total_duration": total_duration, "total_cost": total_cost})

    except Exception as e:
        # If any stage fails, mark the item as error
        update_content_item(content_id, status="error")
        emit_event("pipeline", "error",
                   f"Something went wrong: {str(e)}. This usually means an API key is missing or a service is temporarily down. Check your Settings page.",
                   {"error": str(e)})


# ---------------------------------------------------------------------------
# STAGE 1: SCRAPE
# ---------------------------------------------------------------------------
def stage_scrape(content_id, item, emit_event):
    """Scrape article from URL. Skip if input_type is 'idea'."""
    stage = "scrape"

    if item["input_type"] != "url":
        emit_event(stage, "skipped", "You typed an idea (not a link), so we don't need to go grab an article from the internet. Skipping this step!")
        add_pipeline_log(content_id, stage, "skipped", "Input is an idea, no URL to scrape")
        return 0.0

    start = time.time()
    emit_event(stage, "started", "Sending your link to FireCrawl — it will visit the webpage and pull out just the article text (no ads, no menus, just the good stuff).")
    add_pipeline_log(content_id, stage, "started", f"Scraping: {item['input_text']}")

    update_content_item(content_id, status="scraping")

    result = scrape_url(item["input_text"], emit_event=emit_event)

    duration = round(time.time() - start, 1)

    # Save scraped content to database
    update_content_item(
        content_id,
        status="scraped",
        article_text=result["markdown"],
        article_title=result.get("title", ""),
        word_count=result.get("word_count", 0)
    )

    detail = {
        "duration": duration,
        "word_count": result.get("word_count", 0),
        "title": result.get("title", ""),
        "demo": result.get("demo", False),
        "cost": 0.0
    }

    emit_event(stage, "complete",
               f"Got it! FireCrawl pulled {result.get('word_count', 0):,} words from the article in {duration}s. Now we'll send this text to AI to turn it into a post.",
               detail)
    add_pipeline_log(content_id, stage, "complete",
                     f"Scraped {result.get('word_count', 0)} words", json.dumps(detail))

    return 0.0  # FireCrawl cost is tracked per-account, not per-call


# ---------------------------------------------------------------------------
# STAGE 2: SCRIPT
# ---------------------------------------------------------------------------
def stage_script(content_id, item, emit_event):
    """Generate social media post script via LLM."""
    stage = "script"
    start = time.time()

    emit_event(stage, "started", f"Sending your content to AI (via OpenRouter) to write a {item['platform']} post. Think of OpenRouter as a switchboard — it picks the best AI model for the job.")
    add_pipeline_log(content_id, stage, "started", "Calling OpenRouter LLM")

    update_content_item(content_id, status="scripting")

    # Use article text if available, otherwise use the raw input
    source_text = item.get("article_text") or item["input_text"]
    input_type = item["input_type"]

    result = generate_script(
        source_text,
        platform=item["platform"],
        input_type=input_type,
        emit_event=emit_event
    )

    duration = round(time.time() - start, 1)

    # Save script to database
    update_content_item(content_id, status="scripted", script=result["text"])

    detail = {
        "duration": duration,
        "model": result.get("model", ""),
        "tokens_in": result.get("tokens_in", 0),
        "tokens_out": result.get("tokens_out", 0),
        "cost": result.get("cost", 0.0),
        "demo": result.get("demo", False)
    }

    emit_event(stage, "complete",
               f"Script is done! The AI wrote {result.get('tokens_out', 0)} tokens (words/pieces) in {duration}s. Cost: ${result.get('cost', 0):.4f}. Next up: creating a matching image.",
               detail)
    add_pipeline_log(content_id, stage, "complete",
                     f"Script: {result.get('tokens_out', 0)} tokens", json.dumps(detail))

    return result.get("cost", 0.0)


# ---------------------------------------------------------------------------
# STAGE 3: IMAGE
# ---------------------------------------------------------------------------
def stage_image(content_id, item, emit_event):
    """Generate image: first create a prompt via LLM, then generate via Kie.ai."""
    stage = "image"
    start = time.time()

    emit_event(stage, "started", "Time to create an image! First, AI will describe what the image should look like (a 'prompt'). Then we send that description to Kie.ai, which actually draws the picture.")
    add_pipeline_log(content_id, stage, "started", "Generating image prompt + image")

    update_content_item(content_id, status="imaging")

    # Step 1: Generate an image prompt from the script
    prompt_result = generate_image_prompt(item.get("script", ""), emit_event=emit_event)
    image_prompt = prompt_result["text"]

    # Save the prompt
    update_content_item(content_id, image_prompt=image_prompt)

    # Step 2: Generate the actual image via Kie.ai
    image_result = generate_image(image_prompt, emit_event=emit_event)

    duration = round(time.time() - start, 1)

    # Save image URL and task ID
    update_content_item(
        content_id,
        status="imaged",
        image_url=image_result.get("image_url", ""),
        image_task_id=image_result.get("task_id", "")
    )

    # Total cost = LLM prompt cost + image generation cost
    total_cost = prompt_result.get("cost", 0.0) + image_result.get("cost", 0.0)

    detail = {
        "duration": duration,
        "image_url": image_result.get("image_url", ""),
        "task_id": image_result.get("task_id", ""),
        "prompt_cost": prompt_result.get("cost", 0.0),
        "image_cost": image_result.get("cost", 0.0),
        "total_cost": total_cost,
        "demo": image_result.get("demo", False)
    }

    emit_event(stage, "complete",
               f"Image is ready! It took {duration}s because Kie.ai had to actually render the picture (that's why we kept checking on it). Cost: ${total_cost:.4f}.",
               detail)
    add_pipeline_log(content_id, stage, "complete",
                     f"Image ready: {image_result.get('task_id', 'N/A')}", json.dumps(detail))

    return total_cost


# ---------------------------------------------------------------------------
# STAGE 4: VIDEO (optional)
# ---------------------------------------------------------------------------
def stage_video(content_id, item, emit_event):
    """Generate video via Kie.ai. Skip if include_video is False."""
    stage = "video"

    if not item.get("include_video"):
        emit_event(stage, "skipped", "You didn't ask for a video this time, so we're skipping this step. (Videos take longer and cost more — you can turn this on anytime!)")
        add_pipeline_log(content_id, stage, "skipped", "include_video is False")
        return 0.0

    start = time.time()
    emit_event(stage, "started", "Creating a video with Kie.ai's Veo model. This takes longer than images (sometimes a few minutes) because video has way more frames to generate. Watch the polling — we keep asking 'is it done yet?' every 20 seconds.")
    add_pipeline_log(content_id, stage, "started", "Calling Kie.ai Veo 3.1")

    update_content_item(content_id, status="videoing")

    # Use the image prompt as the video prompt (with slight modification)
    video_prompt = item.get("image_prompt", item.get("script", ""))
    update_content_item(content_id, video_prompt=video_prompt)

    video_result = generate_video(video_prompt, emit_event=emit_event)

    duration = round(time.time() - start, 1)

    update_content_item(
        content_id,
        status="videoed",
        video_url=video_result.get("video_url", ""),
        video_task_id=video_result.get("task_id", "")
    )

    cost = video_result.get("cost", 0.0)

    detail = {
        "duration": duration,
        "video_url": video_result.get("video_url", ""),
        "task_id": video_result.get("task_id", ""),
        "cost": cost,
        "demo": video_result.get("demo", False)
    }

    emit_event(stage, "complete",
               f"Video is done! Took {duration}s (see how much longer than the image?). Cost: ${cost:.4f}. Almost there — just need captions now.",
               detail)
    add_pipeline_log(content_id, stage, "complete",
                     f"Video ready: {video_result.get('task_id', 'N/A')}", json.dumps(detail))

    return cost


# ---------------------------------------------------------------------------
# STAGE 5: CAPTION
# ---------------------------------------------------------------------------
def stage_caption(content_id, item, emit_event):
    """Generate platform-specific captions via LLM."""
    stage = "caption"
    start = time.time()

    emit_event(stage, "started", f"Last step! Each social platform has different rules (character limits, hashtag styles, tone). We're asking AI to write custom captions for {', '.join(platforms)} so each one fits perfectly.")
    add_pipeline_log(content_id, stage, "started", "Calling OpenRouter for captions")

    # Generate captions for the target platform + a few extras
    target = item.get("platform", "instagram")
    platforms = list(set([target, "instagram", "tiktok", "linkedin"]))

    result = generate_captions(
        item.get("script", ""),
        platforms=platforms,
        emit_event=emit_event
    )

    duration = round(time.time() - start, 1)

    # Save captions as JSON
    captions_json = json.dumps(result.get("captions", {}))
    update_content_item(content_id, captions=captions_json)

    cost = result.get("cost", 0.0)

    detail = {
        "duration": duration,
        "platforms": platforms,
        "cost": cost,
        "demo": result.get("demo", False)
    }

    emit_event(stage, "complete",
               f"Captions ready for {len(platforms)} platforms in {duration}s! Each one is tailored — different length, tone, and hashtags for each platform.",
               detail)
    add_pipeline_log(content_id, stage, "complete",
                     f"Captions for {len(platforms)} platforms", json.dumps(detail))

    return cost


# ---------------------------------------------------------------------------
# STAGE 6: PUBLISH (triggered separately)
# ---------------------------------------------------------------------------
def stage_publish(content_id, emit_event):
    """
    Publish content via GetLate.dev.
    This is NOT called by run_pipeline() — it's triggered separately
    via the /api/publish/<id> endpoint.
    """
    stage = "publish"
    start = time.time()

    item = get_content_item(content_id)
    if not item:
        emit_event(stage, "error", f"Content item {content_id} not found")
        return

    emit_event(stage, "started", "Publishing to social media...")
    add_pipeline_log(content_id, stage, "started", "Calling GetLate.dev API")

    update_content_item(content_id, status="publishing")

    try:
        result = publish_post(item, emit_event=emit_event)

        duration = round(time.time() - start, 1)

        update_content_item(
            content_id,
            status="published",
            published_at=datetime.now().isoformat()
        )

        detail = {
            "duration": duration,
            "post_id": result.get("post_id", ""),
            "platforms": result.get("platforms_published", []),
            "demo": result.get("demo", False)
        }

        emit_event(stage, "complete",
                   f"Published in {duration}s!",
                   detail)
        add_pipeline_log(content_id, stage, "complete",
                         f"Published: {result.get('post_id', 'N/A')}", json.dumps(detail))

    except Exception as e:
        update_content_item(content_id, status="error")
        emit_event(stage, "error", f"Publishing failed: {str(e)}")
        add_pipeline_log(content_id, stage, "error", str(e))


# ---------------------------------------------------------------------------
# regenerate_image() — Re-run just the image stage with a new/edited prompt
# ---------------------------------------------------------------------------
def regenerate_image(content_id, new_prompt, emit_event):
    """
    Regenerate the image for a content item using a new prompt.
    Called from the /api/regenerate-image/<id> endpoint.
    """
    emit_event("image", "started", "Regenerating image with updated prompt...")
    add_pipeline_log(content_id, "image", "started", "Regenerating with new prompt")

    start = time.time()

    # Save the new prompt
    update_content_item(content_id, image_prompt=new_prompt)

    # Generate new image
    result = generate_image(new_prompt, emit_event=emit_event)

    duration = round(time.time() - start, 1)

    update_content_item(
        content_id,
        image_url=result.get("image_url", ""),
        image_task_id=result.get("task_id", "")
    )

    detail = {
        "duration": duration,
        "image_url": result.get("image_url", ""),
        "task_id": result.get("task_id", ""),
        "cost": result.get("cost", 0.0),
        "demo": result.get("demo", False)
    }

    emit_event("image", "complete",
               f"Image regenerated in {duration}s",
               detail)
    add_pipeline_log(content_id, "image", "complete",
                     f"Regenerated: {result.get('task_id', 'N/A')}", json.dumps(detail))
