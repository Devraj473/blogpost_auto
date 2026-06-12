import os
import sys
from datetime import datetime

from src.config import load_config
from src.logger import setup_logger
from src.ai.groq_client import GroqClient
from src.image.pexels_client import PexelsClient
from src.story.generator import StoryGenerator
from src.storage.file_storage import FileStorage
from src.email_sender.smtp_sender import SMTPSender

logger = setup_logger("orchestrator")

def run_daily_workflow():
    logger.info("=== ITSSTORYDAY DAILY AUTOMATION WORKFLOW STARTED ===")
    
    # 1. Load Configuration
    try:
        config = load_config()
        logger.info("Configuration loaded and validated.")
    except Exception as e:
        logger.critical(f"Workflow aborted: Configuration failure: {e}")
        sys.exit(1)

    # 2. Initialize Clients
    try:
        ai_client = GroqClient(api_key=config.groq_api_key, model=config.groq_model)
        pexels_client = PexelsClient(api_key=config.pexels_api_key)
        storage = FileStorage()
        email_sender = SMTPSender(config)
        generator = StoryGenerator(config, ai_client)
        logger.info("All workflow clients and handlers initialized.")
    except Exception as e:
        logger.critical(f"Workflow aborted: Clients initialization failure: {e}")
        sys.exit(1)

    # 3. Select Category
    try:
        category, category_idx = generator.select_category()
        logger.info(f"Selected category: {category} (Index: {category_idx})")
    except Exception as e:
        logger.error(f"Failed to select category: {e}")
        # Default to first category as fallback
        category, category_idx = "AI Stories & Ideas", 0
        logger.info(f"Falling back to category: {category}")

    # 4. Generate unique topic
    topic = None
    try:
        recent_topics = generator.get_recent_topics(limit=5)
        topic = generator.generate_topic(category, recent_topics)
        logger.info(f"Generated Topic: '{topic.title}'")
        logger.info(f"Premise: '{topic.premise}'")
        logger.info(f"Pexels search term: '{topic.pexels_query}'")
    except Exception as e:
        logger.critical(f"Workflow aborted: Topic generation failed: {e}")
        sys.exit(1)

    # 5. Fetch visual asset from Pexels
    pexels_image_data = None
    try:
        # We query with the specific topic query and category name as fallback
        pexels_image_data = pexels_client.search_photo(
            query=topic.pexels_query,
            fallback_query=category
        )
        if pexels_image_data:
            logger.info("Fetched image from Pexels.")
            logger.info(f"Featured: {pexels_image_data['featured']}")
            logger.info(f"Attribution: Photo by {pexels_image_data['photographer']}")
        else:
            logger.warning("No image found on Pexels. Proceeding without featured image.")
    except Exception as e:
        logger.error(f"Error querying Pexels: {e}. Proceeding without image.")

    # 6. Generate Story
    story = None
    try:
        story = generator.generate_story(category, topic)
        logger.info("Successfully generated story content.")
    except Exception as e:
        logger.critical(f"Workflow aborted: Story generation failed: {e}")
        sys.exit(1)

    # 7. Save Files
    saved_dir = ""
    try:
        saved_dir = storage.save_story(category, story, pexels_image_data)
        logger.info(f"Successfully saved all output files to directory: {saved_dir}")
    except Exception as e:
        logger.error(f"Error saving files: {e}. Continuing with email dispatch.")

    # 8. Dispatch Email
    try:
        # Load rendered HTML content from story.html if it exists
        html_body = ""
        html_file_path = os.path.join(saved_dir, "story.html") if saved_dir else ""
        if html_file_path and os.path.exists(html_file_path):
            with open(html_file_path, "r", encoding="utf-8") as f:
                html_body = f.read()
        
        # If html file is not available, we construct a simple one
        if not html_body:
            logger.warning("story.html not found. Using simple fallback HTML for email body.")
            html_body = f"<h1>{story.seo_title}</h1><p>{story.introduction}</p><p>{story.story_content}</p>"

        # Prepare Text-only alternative body
        text_body = (
            f"=== NEW STORY BLOG GENERATED ===\n"
            f"Category: {category}\n"
            f"Title: {story.seo_title}\n"
            f"Focus Keyword: {story.focus_keyword}\n"
            f"URL Slug: {story.url_slug}\n"
            f"Meta Description: {story.meta_description}\n\n"
            f"--- INTRODUCTION ---\n"
            f"{story.introduction}\n\n"
            f"--- STORY CONTENT ---\n"
            f"{story.story_content.replace('<p>', '').replace('</p>', '\n\n')}\n\n"
            f"--- MORAL LESSON ---\n"
            f"{story.moral_lesson}\n\n"
            f"--- READER REFLECTIONS ---\n"
            f"{chr(10).join(['- ' + q for q in story.reader_reflection])}\n\n"
            f"--- FAQ SECTION ---\n"
            f"{chr(10).join([item.question + chr(10) + item.answer for item in story.faq])}\n\n"
            f"--- AI IMAGE PROMPTS ---\n"
            f"Featured Image Prompt: {story.featured_image_prompt}\n"
            f"Thumbnail Prompt: {story.thumbnail_prompt}\n"
            f"Pinterest Prompt: {story.pinterest_image_prompt}\n"
        )

        subject = f"New Story Blog Generated - {story.seo_title}"
        email_sender.send_email(
            subject=subject,
            html_body=html_body,
            text_body=text_body
        )
        logger.info("Email delivery complete.")
    except Exception as e:
        logger.error(f"Failed to deliver email: {e}")

    # 9. Commit Category Rotation State
    try:
        generator.update_state(category_idx)
        logger.info("Category state rotation complete.")
    except Exception as e:
        logger.error(f"Failed to update category rotation index state: {e}")

    logger.info("=== ITSSTORYDAY DAILY AUTOMATION WORKFLOW COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_daily_workflow()
