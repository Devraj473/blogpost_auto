import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader

from src.logger import setup_logger
from src.story.models import StoryResponse

logger = setup_logger("file_storage")

class FileStorage:
    """
    Handles saving generated stories and metadata into the blogs/YYYY/MM/DD/ directory structure.
    """
    def __init__(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.blogs_dir = os.path.join(self.root_dir, "blogs")
        self.templates_dir = os.path.join(self.root_dir, "templates")
        
        logger.info(f"FileStorage initialized with blogs dir: {self.blogs_dir}")

    def save_story(
        self, 
        category: str, 
        story: StoryResponse, 
        pexels_data: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Saves the story files: story.md, story.html, metadata.json, and image_prompt.txt.
        Returns the absolute path to the directory where files are stored.
        """
        # Calculate YYYY/MM/DD path
        now = datetime.now()
        date_path = now.strftime("%Y/%m/%d")
        dest_dir = os.path.join(self.blogs_dir, now.strftime("%Y"), now.strftime("%m"), now.strftime("%d"))
        os.makedirs(dest_dir, exist_ok=True)
        
        logger.info(f"Saving story files to target directory: {dest_dir}")

        image_url = pexels_data.get("featured", "") if pexels_data else ""
        photographer = pexels_data.get("photographer", "") if pexels_data else ""
        photographer_url = pexels_data.get("photographer_url", "") if pexels_data else ""

        # 1. Save metadata.json
        meta_content = {
            "category": category,
            "title": story.seo_title,
            "seo_title": story.seo_title,
            "meta_description": story.meta_description,
            "focus_keyword": story.focus_keyword,
            "related_keywords": story.related_keywords,
            "seo_tags": story.seo_tags,
            "url_slug": story.url_slug,
            "date": now.strftime("%Y-%m-%d %H:%M:%S"),
            "image": {
                "url": image_url,
                "photographer": photographer,
                "photographer_url": photographer_url
            },
            "prompts": {
                "featured": story.featured_image_prompt,
                "thumbnail": story.thumbnail_prompt,
                "pinterest": story.pinterest_image_prompt
            }
        }
        
        meta_file = os.path.join(dest_dir, "metadata.json")
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(meta_content, f, indent=2, ensure_ascii=False)
        logger.info("metadata.json written successfully.")

        # 2. Save image_prompt.txt
        prompts_file = os.path.join(dest_dir, "image_prompt.txt")
        with open(prompts_file, "w", encoding="utf-8") as f:
            f.write(f"Featured Image Prompt (16:9):\n{story.featured_image_prompt}\n\n")
            f.write(f"Thumbnail Prompt (1:1):\n{story.thumbnail_prompt}\n\n")
            f.write(f"Pinterest Image Prompt (2:3):\n{story.pinterest_image_prompt}\n")
        logger.info("image_prompt.txt written successfully.")

        # 3. Save story.md
        md_file = os.path.join(dest_dir, "story.md")
        # Strip HTML tags from content for Markdown representation (simple clean)
        clean_markdown_body = story.story_content
        # Let's replace simple HTML tags with markdown for readability in md
        clean_markdown_body = clean_markdown_body.replace("<p>", "").replace("</p>", "\n\n")
        clean_markdown_body = clean_markdown_body.replace("<strong>", "**").replace("</strong>", "**")
        clean_markdown_body = clean_markdown_body.replace("<em>", "*").replace("</em>", "*")
        
        md_content = f"""# {story.seo_title}

**Category:** {category}  
**Date:** {now.strftime("%Y-%m-%d")}  
**Focus Keyword:** {story.focus_keyword}  
**URL Slug:** {story.url_slug}  

---

## Introduction
{story.introduction}

---

## Story
{clean_markdown_body}

---

## Moral Lesson
> {story.moral_lesson}

---

## Reader Reflection
{chr(10).join([f'- {q}' for q in story.reader_reflection])}

---

## FAQ
{chr(10).join([f'### {item.question}{chr(10)}{item.answer}{chr(10)}' for item in story.faq])}
"""
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)
        logger.info("story.md written successfully.")

        # 4. Save story.html (Rendered email template or web page)
        html_file = os.path.join(dest_dir, "story.html")
        try:
            env = Environment(loader=FileSystemLoader(self.templates_dir))
            template = env.get_template("email_template.html")
            
            rendered_html = template.render(
                category=category,
                story_title=story.seo_title,
                meta_description=story.meta_description,
                introduction=story.introduction,
                story_content=story.story_content,
                moral_lesson=story.moral_lesson,
                reader_reflection=story.reader_reflection,
                faq=[{"question": item.question, "answer": item.answer} for item in story.faq],
                focus_keyword=story.focus_keyword,
                url_slug=story.url_slug,
                related_keywords=story.related_keywords,
                seo_tags=story.seo_tags,
                featured_image_prompt=story.featured_image_prompt,
                thumbnail_prompt=story.thumbnail_prompt,
                pinterest_image_prompt=story.pinterest_image_prompt,
                image_url=image_url,
                photographer=photographer,
                photographer_url=photographer_url
            )
            
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(rendered_html)
            logger.info("story.html written successfully.")
            
        except Exception as e:
            logger.error(f"Failed to generate story.html: {e}")
            # Write a simple fallback HTML if rendering fails
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(f"<h1>{story.seo_title}</h1><p>{story.story_content}</p>")

        return dest_dir
