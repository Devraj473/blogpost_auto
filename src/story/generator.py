import os
import json
import random
from datetime import datetime
from typing import List, Tuple, Optional

from src.config import AppConfig
from src.logger import setup_logger
from src.ai.base import BaseAIClient
from src.story.models import TopicResponse, StoryResponse, StoryMetadataResponse
from src.story.prompts import load_prompt_template

logger = setup_logger("story_generator")

CATEGORIES = [
    "AI Stories & Ideas",
    "AI Project Ideas",
    "AI Prompts & Tools",
    "Machine Learning Tips",
    "Generative AI Trends",
    "AI Career Insights",
    "AI Applications & Use Cases",
    "AI Ethics & Safety",
    "AI News & Updates",
    "Prompt Engineering Guides"
]

class StoryGenerator:
    """
    Manages the selection of categories, generation of topics, and writing of stories.
    """
    def __init__(self, config: AppConfig, ai_client: BaseAIClient):
        self.config = config
        self.ai_client = ai_client
        
        # Root directories
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.state_file = os.path.join(self.root_dir, "config", "state.json")
        self.blogs_dir = os.path.join(self.root_dir, "blogs")
        
        logger.info("StoryGenerator initialized.")

    def select_category(self) -> Tuple[str, int]:
        """
        Selects a category based on the configured method (sequential or random).
        Returns the category name and its index.
        """
        method = self.config.category_selection_method
        logger.info(f"Selecting category using method: '{method}'")

        if method == "random":
            idx = random.randint(0, len(CATEGORIES) - 1)
            category = CATEGORIES[idx]
            return category, idx

        # Sequential method (default)
        last_idx = -1
        state_data = {}
        
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    state_data = json.load(f)
                    last_idx = state_data.get("last_category_index", -1)
            except Exception as e:
                logger.warning(f"Could not read state file: {e}. Starting from index 0.")

        next_idx = (last_idx + 1) % len(CATEGORIES)
        category = CATEGORIES[next_idx]
        
        logger.info(f"Selected category: '{category}' (index: {next_idx}, previous: {last_idx})")
        return category, next_idx

    def update_state(self, category_index: int):
        """
        Updates the state file with the last index and run date.
        """
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        state_data = {
            "last_category_index": category_index,
            "last_run_date": datetime.now().strftime("%Y-%m-%d")
        }
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state_data, f, indent=2)
            logger.info("Category state file updated successfully.")
        except Exception as e:
            logger.error(f"Failed to update state file: {e}")

    def get_recent_topics(self, limit: int = 5) -> List[str]:
        """
        Scans the blogs/ folder recursively to find previously generated story titles
        to pass to the AI topic generator (avoiding repetition).
        """
        recent_titles = []
        if not os.path.exists(self.blogs_dir):
            return []

        metadata_files = []
        # Walk blogs dir to collect metadata paths
        for root, _, files in os.walk(self.blogs_dir):
            for file in files:
                if file == "metadata.json":
                    metadata_files.append(os.path.join(root, file))

        # Sort files by path name (which has YYYY/MM/DD structure, giving chronological sort)
        metadata_files.sort(reverse=True)

        for file_path in metadata_files[:limit]:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    title = meta.get("title", meta.get("seo_title", ""))
                    if title:
                        recent_titles.append(title)
            except Exception as e:
                logger.warning(f"Error parsing metadata file {file_path}: {e}")

        logger.info(f"Retrieved recent topics for deduplication: {recent_titles}")
        return recent_titles

    def generate_topic(self, category: str, recent_topics: List[str]) -> TopicResponse:
        """
        Generates a unique story topic and premise using AI.
        """
        logger.info(f"Generating story topic for category: '{category}'...")
        system_prompt = "You are an AI education editorial planner for ItsStoryDay blog."
        
        # Load and format topic generator prompt
        raw_template = load_prompt_template("topic_generator.txt")
        recent_topics_str = "\n".join([f"- {t}" for t in recent_topics]) if recent_topics else "None"
        user_prompt = raw_template.format(
            category=category,
            recent_topics=recent_topics_str
        )

        # Generate using Groq client
        topic: TopicResponse = self.ai_client.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=TopicResponse,
            temperature=0.85
        )
        logger.info(f"Topic generated: '{topic.title}' with query keyword: '{topic.pexels_query}'")
        return topic

    def generate_story(self, category: str, topic: TopicResponse) -> StoryResponse:
        """
        Generates the full story based on category and topic.
        Uses a two-step generation process: first metadata, then narrative.
        """
        # Step 1: Generate Metadata and Outline
        logger.info(f"Step 1: Generating metadata and story outline for '{topic.title}'...")
        system_prompt_meta = (
            "You are an expert AI educator and professional SEO content writer. "
            "Your task is to generate complete, high-quality SEO metadata, tags, and a structured content outline."
        )
        raw_meta_template = load_prompt_template("metadata_generator.txt")
        user_prompt_meta = raw_meta_template.format(
            category=category,
            topic_title=topic.title,
            topic_premise=topic.premise
        )
        
        metadata: StoryMetadataResponse = self.ai_client.generate_json(
            system_prompt=system_prompt_meta,
            user_prompt=user_prompt_meta,
            response_model=StoryMetadataResponse,
            temperature=0.75
        )
        logger.info("Successfully generated metadata and story outline.")

        # Step 2: Generate Story Narrative
        logger.info(f"Step 2: Generating full narrative text (1500-3000 words)...")
        system_prompt_story = (
            "You are an expert AI educator and technical writer who creates practical, clear, and engaging long-form guides. "
            "You write with real-world examples, actionable steps, and beginner-friendly explanations."
        )
        raw_story_template = load_prompt_template("story_generator.txt")
        user_prompt_story = raw_story_template.format(
            category=category,
            topic_title=topic.title,
            topic_premise=topic.premise,
            introduction=metadata.introduction,
            story_outline=metadata.story_outline
        )
        
        narrative = self.ai_client.generate_text(
            system_prompt=system_prompt_story,
            user_prompt=user_prompt_story,
            temperature=0.75
        )
        
        word_count = len(narrative.split())
        logger.info(f"Successfully generated narrative of {word_count} words.")
        
        # Enforce minimum word count check (retry once if it fails to hit 1000)
        if word_count < 1000:
            logger.warning(f"Narrative is slightly short ({word_count} words). Requesting expansion...")
            user_prompt_expand = (
                f"Your previous draft was only {word_count} words. "
                f"Please rewrite it to be significantly longer, more detailed, and at least 1500 words. "
                f"Write out all sections in full, expand explanations and examples, and add practical implementation details. "
                f"Here was the outline:\n{metadata.story_outline}\n\n"
                f"And here was your draft:\n{narrative}"
            )
            try:
                expanded_narrative = self.ai_client.generate_text(
                    system_prompt=system_prompt_story,
                    user_prompt=user_prompt_expand,
                    temperature=0.75
                )
                expanded_word_count = len(expanded_narrative.split())
                if expanded_word_count > word_count:
                    narrative = expanded_narrative
                    word_count = expanded_word_count
                    logger.info(f"Successfully expanded narrative to {word_count} words.")
            except Exception as e:
                logger.error(f"Expansion failed: {e}. Keeping original draft.")

        # Combine into StoryResponse container
        story = StoryResponse(
            seo_title=metadata.seo_title,
            meta_description=metadata.meta_description,
            focus_keyword=metadata.focus_keyword,
            related_keywords=metadata.related_keywords,
            seo_tags=metadata.seo_tags,
            url_slug=metadata.url_slug,
            introduction=metadata.introduction,
            story_content=narrative,
            moral_lesson=metadata.moral_lesson,
            reader_reflection=metadata.reader_reflection,
            faq=metadata.faq,
            featured_image_prompt=metadata.featured_image_prompt,
            thumbnail_prompt=metadata.thumbnail_prompt,
            pinterest_image_prompt=metadata.pinterest_image_prompt
        )
        
        return story
