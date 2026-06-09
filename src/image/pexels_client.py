import requests
import logging
from typing import Dict, Optional
from src.logger import setup_logger

logger = setup_logger("pexels_client")

class PexelsClient:
    """
    Pexels Client to search for and retrieve free stock photos for stories.
    """
    BASE_URL = "https://api.pexels.com/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": self.api_key
        }
        logger.info("PexelsClient initialized.")

    def search_photo(self, query: str, fallback_query: Optional[str] = None) -> Optional[Dict[str, str]]:
        """
        Searches Pexels for a photo matching the query.
        Returns a dictionary of URLs for different sizes:
        {
            "featured": url,
            "thumbnail": url,
            "pinterest": url,
            "photographer": name,
            "photographer_url": url
        }
        
        If no photos are found and fallback_query is provided, searches for the fallback.
        """
        url = f"{self.BASE_URL}/search"
        params = {
            "query": query,
            "per_page": 1,
            "page": 1
        }

        try:
            logger.info(f"Querying Pexels API for '{query}'...")
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                photos = data.get("photos", [])
                
                if photos:
                    photo = photos[0]
                    src = photo.get("src", {})
                    logger.info(f"Pexels search match found: ID {photo.get('id')}")
                    return {
                        "featured": src.get("landscape", src.get("large", "")),
                        "thumbnail": src.get("medium", ""),
                        "pinterest": src.get("portrait", src.get("large", "")),
                        "photographer": photo.get("photographer", "Unknown"),
                        "photographer_url": photo.get("photographer_url", "")
                    }
                else:
                    logger.warning(f"No photos found for query: '{query}'")
            else:
                logger.error(f"Pexels API error: Status Code {response.status_code}, Body: {response.text}")

        except Exception as e:
            logger.error(f"Failed to query Pexels API: {e}")

        # Try fallback if available
        if fallback_query and fallback_query != query:
            logger.info(f"Retrying Pexels search with fallback query: '{fallback_query}'")
            return self.search_photo(fallback_query, fallback_query=None)

        return None
