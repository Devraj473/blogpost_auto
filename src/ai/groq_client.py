import json
import time
import logging
from typing import Type
from pydantic import BaseModel
from groq import Groq

from src.ai.base import BaseAIClient
from src.logger import setup_logger

logger = setup_logger("groq_client")

class GroqClient(BaseAIClient):
    """
    Client for Groq's LLM APIs.
    Inherits from BaseAIClient and provides JSON mode completions with validation.
    """
    def __init__(self, api_key: str, model: str = "llama-3-70b-8192"):
        self.api_key = api_key
        self.model = model
        self.client = Groq(api_key=self.api_key)
        logger.info(f"Initialized Groq client with model: {self.model}")

    def generate_json(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        response_model: Type[BaseModel],
        temperature: float = 0.7
    ) -> BaseModel:
        """
        Calls Groq API in JSON mode and parses the result into the response_model.
        Includes an automatic retry mechanism with exponential backoff.
        """
        max_retries = 3
        backoff_factor = 2.0
        
        # We append schema instructions to system prompt to guide LLM schema generation
        schema_json = json.dumps(response_model.model_json_schema(), indent=2)
        enriched_system_prompt = (
            f"{system_prompt}\n\n"
            f"You MUST return a JSON object that matches this JSON Schema:\n"
            f"{schema_json}\n"
            f"Do not include any introductory or concluding text, only return the JSON object."
        )

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Sending request to Groq (Attempt {attempt}/{max_retries})...")
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": enriched_system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=temperature,
                )
                
                raw_content = completion.choices[0].message.content
                logger.debug(f"Raw response from Groq: {raw_content}")
                
                # Parse and validate JSON
                parsed_data = json.loads(raw_content)
                validated_model = response_model.model_validate(parsed_data)
                logger.info("Successfully generated and validated JSON response from Groq.")
                return validated_model
                
            except json.JSONDecodeError as jde:
                logger.warning(f"Attempt {attempt} failed - invalid JSON returned: {jde}")
            except Exception as e:
                logger.warning(f"Attempt {attempt} failed - Groq API call error: {e}")
            
            if attempt < max_retries:
                sleep_time = backoff_factor ** attempt
                logger.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
        
        # If all retries failed, raise a final exception
        raise RuntimeError("Failed to generate a valid structured response from Groq after multiple attempts.")

    def generate_text(
        self, 
        system_prompt: str, 
        user_prompt: str,
        temperature: float = 0.7
    ) -> str:
        """
        Calls Groq API to generate standard raw text.
        Includes an automatic retry mechanism with exponential backoff.
        """
        max_retries = 3
        backoff_factor = 2.0

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Sending text request to Groq (Attempt {attempt}/{max_retries})...")
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature,
                )
                
                content = completion.choices[0].message.content
                if content and content.strip():
                    logger.info("Successfully generated raw text response from Groq.")
                    return content
                else:
                    logger.warning(f"Attempt {attempt} returned empty content.")
                
            except Exception as e:
                logger.warning(f"Attempt {attempt} failed - Groq API call error: {e}")
            
            if attempt < max_retries:
                sleep_time = backoff_factor ** attempt
                logger.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
        
        raise RuntimeError("Failed to generate text response from Groq after multiple attempts.")
