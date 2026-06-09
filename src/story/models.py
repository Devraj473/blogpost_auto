from typing import List
from pydantic import BaseModel, Field, field_validator

class TopicResponse(BaseModel):
    """
    Data model for the generated story topic.
    """
    title: str = Field(description="Captivating literary title of the story.")
    premise: str = Field(description="A 1-2 sentence compelling summary of the narrative plot.")
    pexels_query: str = Field(description="Concrete scene keywords for searching free stock images on Pexels.")

    @field_validator("title", "premise", "pexels_query")
    @classmethod
    def clean_strings(cls, v: str) -> str:
        return v.strip().strip("'\"")

class FAQItem(BaseModel):
    """
    FAQ Question & Answer pair.
    """
    question: str = Field(description="A common reader question related to the story or moral lesson.")
    answer: str = Field(description="A detailed and helpful answer answering the question.")

class StoryResponse(BaseModel):
    """
    Pydantic model representing the full SEO-optimized story blog post.
    """
    seo_title: str = Field(description="SEO Optimized Title (under 60 characters).")
    meta_description: str = Field(description="SEO Meta Description (under 160 characters).")
    focus_keyword: str = Field(description="Primary focus keyword.")
    related_keywords: List[str] = Field(description="Exactly 15 highly searched related keywords.")
    seo_tags: List[str] = Field(description="Exactly 15 relevant tags.")
    url_slug: str = Field(description="Lowercase, hyphenated slug for the URL.")
    introduction: str = Field(description="Compelling introduction hook (under 150 words).")
    story_content: str = Field(description="Full story narrative (1500-3000 words, rich with HTML paragraphs).")
    moral_lesson: str = Field(description="Moral or key takeaway written naturally.")
    reader_reflection: List[str] = Field(description="2 to 3 thought-provoking questions to invite comments.")
    faq: List[FAQItem] = Field(description="At least 3 relevant FAQs.")
    featured_image_prompt: str = Field(description="AI Image generator prompt for Featured landscape image (16:9).")
    thumbnail_prompt: str = Field(description="AI Image generator prompt for square thumbnail image (1:1).")
    pinterest_image_prompt: str = Field(description="AI Image generator prompt for Pinterest vertical image (2:3).")

    @field_validator("related_keywords", "seo_tags")
    @classmethod
    def validate_list_size(cls, v: List[str], info) -> List[str]:
        # Filter empty strings and clean whitespaces
        cleaned_list = [item.strip() for item in v if item.strip()]
        if len(cleaned_list) < 15:
            name = info.field_name
            while len(cleaned_list) < 15:
                cleaned_list.append(f"story {name.replace('_', ' ')} {len(cleaned_list) + 1}")
        return cleaned_list[:15]

    @field_validator("faq")
    @classmethod
    def validate_faq_size(cls, v: List[FAQItem]) -> List[FAQItem]:
        if len(v) < 3:
            raise ValueError(f"FAQ must contain at least 3 items, got {len(v)}.")
        return v

    @field_validator("story_content")
    @classmethod
    def validate_word_count(cls, v: str) -> str:
        # Approximate word count
        words = v.split()
        word_count = len(words)
        if word_count < 1000:
            # The prompt requested 1500-3000 words. Let's enforce at least 1000 words strictly
            # to accommodate model variance, but raise if it's too short (like a brief outline).
            raise ValueError(f"Story word count is too short ({word_count} words). Must be at least 1000 words.")
        return v

class StoryMetadataResponse(BaseModel):
    """
    Pydantic model representing the metadata and outline of the story blog post.
    """
    seo_title: str = Field(description="SEO Optimized Title (under 60 characters).")
    meta_description: str = Field(description="SEO Meta Description (under 160 characters).")
    focus_keyword: str = Field(description="Primary focus keyword.")
    related_keywords: List[str] = Field(description="Exactly 15 highly searched related keywords.")
    seo_tags: List[str] = Field(description="Exactly 15 relevant tags.")
    url_slug: str = Field(description="Lowercase, hyphenated slug for the URL.")
    introduction: str = Field(description="Compelling introduction hook (under 150 words).")
    moral_lesson: str = Field(description="Moral or key takeaway written naturally.")
    reader_reflection: List[str] = Field(description="2 to 3 thought-provoking questions to invite comments.")
    faq: List[FAQItem] = Field(description="At least 3 relevant FAQs.")
    featured_image_prompt: str = Field(description="AI Image generator prompt for Featured landscape image (16:9).")
    thumbnail_prompt: str = Field(description="AI Image generator prompt for square thumbnail image (1:1).")
    pinterest_image_prompt: str = Field(description="AI Image generator prompt for Pinterest vertical image (2:3).")
    story_outline: str = Field(description="A brief chapter outline of the story (e.g. Chapter 1: ..., Chapter 2: ...) to guide narrative generation.")

    @field_validator("related_keywords", "seo_tags")
    @classmethod
    def validate_list_size(cls, v: List[str], info) -> List[str]:
        cleaned_list = [item.strip() for item in v if item.strip()]
        if len(cleaned_list) < 15:
            name = info.field_name
            while len(cleaned_list) < 15:
                cleaned_list.append(f"story {name.replace('_', ' ')} {len(cleaned_list) + 1}")
        return cleaned_list[:15]

    @field_validator("faq")
    @classmethod
    def validate_faq_size(cls, v: List[FAQItem]) -> List[FAQItem]:
        if len(v) < 3:
            raise ValueError(f"FAQ must contain at least 3 items, got {len(v)}.")
        return v
