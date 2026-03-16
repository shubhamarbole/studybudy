from django.core.cache import cache
import os
from transformers import pipeline
from django.core.cache import cache

class ToxicityChecker:
    def __init__(self):
        self.toxic_words = self._load_toxic_words()
        
    def _load_toxic_words(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(base_dir, 'utils', 'toxic_words.txt')) as f:
            return [line.strip().lower() for line in f if line.strip()]
    
    def is_toxic(self, text):
        text_lower = text.lower()
        
        # Exact phrase matching
        if any(phrase in text_lower for phrase in self.toxic_words):
            return True
            
        # Optional: Word boundary matching (more strict)
        # import re
        # if any(re.search(rf'\b{word}\b', text_lower) for word in self.toxic_words):
        #     return True
            
        return False

toxicity_checker = ToxicityChecker()