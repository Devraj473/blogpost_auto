import os
import json
import unittest
from unittest.mock import MagicMock, patch

from src.config import AppConfig
from src.story.generator import StoryGenerator, CATEGORIES

class TestStoryGenerator(unittest.TestCase):
    
    def setUp(self):
        # Base config mock
        self.config = AppConfig(
            groq_api_key="mock_key_mock_key_mock_key_mock_key",
            pexels_api_key="mock_key_mock_key_mock_key_mock_key",
            smtp_email="mock@gmail.com",
            smtp_password="mock",
            recipient_email="mock@gmail.com"
        )
        self.ai_client = MagicMock()
        
    def test_category_selection_sequential(self):
        """
        Verifies that sequential category selection increments index and cycles.
        """
        # We patch the state file path to a temp file
        temp_state_file = "config/state_test.json"
        
        generator = StoryGenerator(self.config, self.ai_client)
        generator.state_file = temp_state_file
        
        # Ensure file starts clean
        if os.path.exists(temp_state_file):
            os.remove(temp_state_file)
            
        try:
            # 1. First run, no state file. Should pick index 0 (Motivational Stories)
            category, idx = generator.select_category()
            self.assertEqual(category, CATEGORIES[0])
            self.assertEqual(idx, 0)
            
            # Save the index to state file
            generator.update_state(idx)
            
            # Verify file was written
            self.assertTrue(os.path.exists(temp_state_file))
            with open(temp_state_file, "r") as f:
                data = json.load(f)
                self.assertEqual(data["last_category_index"], 0)
                
            # 2. Second run. Should read state file and pick index 1 (Moral Stories)
            category, idx = generator.select_category()
            self.assertEqual(category, CATEGORIES[1])
            self.assertEqual(idx, 1)
            
            generator.update_state(idx)
            
            # 3. Set index to last category index (len - 1) and test roll-over to 0
            generator.update_state(len(CATEGORIES) - 1)
            category, idx = generator.select_category()
            self.assertEqual(category, CATEGORIES[0])
            self.assertEqual(idx, 0)
            
        finally:
            # Clean up test state file
            if os.path.exists(temp_state_file):
                os.remove(temp_state_file)

    def test_category_selection_random(self):
        """
        Verifies that random category selection returns a valid category.
        """
        self.config.category_selection_method = "random"
        generator = StoryGenerator(self.config, self.ai_client)
        
        category, idx = generator.select_category()
        self.assertIn(category, CATEGORIES)
        self.assertTrue(0 <= idx < len(CATEGORIES))

if __name__ == "__main__":
    unittest.main()
