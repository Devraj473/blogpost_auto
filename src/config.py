import os
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class AppConfig(BaseModel):
    """
    Configuration settings for ItsStoryDay Automation Platform.
    Loads values from environment variables and performs basic validation.
    """
    groq_api_key: str = Field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    groq_model: str = Field(default_factory=lambda: os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))
    pexels_api_key: str = Field(default_factory=lambda: os.getenv("PEXELS_API_KEY", ""))
    
    # SMTP Configuration
    smtp_server: str = Field(default_factory=lambda: os.getenv("SMTP_SERVER", "smtp.gmail.com"))
    smtp_port: int = Field(default_factory=lambda: int(os.getenv("SMTP_PORT", "587")))
    smtp_email: str = Field(default_factory=lambda: os.getenv("SMTP_EMAIL", ""))
    smtp_password: str = Field(default_factory=lambda: os.getenv("SMTP_PASSWORD", ""))
    recipient_email: str = Field(default_factory=lambda: os.getenv("RECIPIENT_EMAIL", ""))
    
    # Content Settings
    blog_length_min: int = Field(default_factory=lambda: int(os.getenv("BLOG_LENGTH_MIN", "1500")))
    blog_length_max: int = Field(default_factory=lambda: int(os.getenv("BLOG_LENGTH_MAX", "3000")))
    category_selection_method: str = Field(default_factory=lambda: os.getenv("CATEGORY_SELECTION_METHOD", "sequential"))

    @field_validator("groq_api_key", "pexels_api_key", "smtp_email", "smtp_password", "recipient_email")
    @classmethod
    def check_non_empty(cls, v: str, info) -> str:
        clean_val = v.strip().strip("'\"")
        if not clean_val:
            raise ValueError(f"Environment variable for '{info.field_name.upper()}' is not set or empty.")
        return clean_val

    @field_validator("category_selection_method")
    @classmethod
    def check_method(cls, v: str) -> str:
        allowed = ["sequential", "random"]
        if v.lower() not in allowed:
            raise ValueError(f"CATEGORY_SELECTION_METHOD must be one of {allowed}, got '{v}'")
        return v.lower()

def load_config() -> AppConfig:
    """Helper method to load and validate configuration."""
    try:
        return AppConfig()
    except Exception as e:
        print(f"Configuration Loading Error: {e}")
        raise
