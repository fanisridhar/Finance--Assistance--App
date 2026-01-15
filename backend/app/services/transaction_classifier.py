from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Tuple, Optional
import json

# Predefined categories with sample transaction descriptions
CATEGORY_EXAMPLES = {
    "Food and Drink": [
        "restaurant", "cafe", "coffee", "groceries", "food", "dining", "pizza", "burger",
        "starbucks", "mcdonald", "subway", "walmart", "target", "whole foods"
    ],
    "Transportation": [
        "uber", "lyft", "taxi", "gas", "fuel", "parking", "metro", "subway", "bus",
        "train", "airline", "flight", "car rental", "toll"
    ],
    "Shopping": [
        "amazon", "ebay", "store", "mall", "retail", "clothing", "apparel", "electronics"
    ],
    "Entertainment": [
        "netflix", "spotify", "movie", "cinema", "theater", "concert", "game", "sports",
        "streaming", "subscription"
    ],
    "Bills and Utilities": [
        "electric", "water", "gas bill", "internet", "phone", "cable", "utility",
        "electricity", "power"
    ],
    "Healthcare": [
        "pharmacy", "hospital", "doctor", "medical", "dental", "insurance", "cvs",
        "walgreens", "clinic"
    ],
    "Education": [
        "tuition", "school", "university", "course", "education", "textbook", "student"
    ],
    "Travel": [
        "hotel", "booking", "airbnb", "travel", "vacation", "trip", "resort"
    ],
    "Personal Care": [
        "salon", "barber", "spa", "gym", "fitness", "beauty", "cosmetics"
    ],
    "General": [
        "atm", "transfer", "payment", "fee", "charge"
    ]
}

class TransactionClassifier:
    def __init__(self):
        # Load a lightweight sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.category_embeddings = self._build_category_embeddings()
    
    def _build_category_embeddings(self) -> Dict[str, np.ndarray]:
        """Build embeddings for each category based on example transactions"""
        category_embeddings = {}
        for category, examples in CATEGORY_EXAMPLES.items():
            # Create embeddings for all examples in the category
            example_embeddings = self.model.encode(examples)
            # Average the embeddings to get a category representation
            category_embeddings[category] = np.mean(example_embeddings, axis=0)
        return category_embeddings
    
    def classify_transaction(
        self, 
        transaction_name: str, 
        merchant_name: Optional[str] = None
    ) -> Tuple[str, float]:
        """
        Classify a transaction and return the category and confidence score.
        
        Args:
            transaction_name: The transaction name/description
            merchant_name: Optional merchant name
            
        Returns:
            Tuple of (category, confidence_score)
        """
        # Combine transaction name and merchant name for better classification
        text = transaction_name.lower()
        if merchant_name:
            text += " " + merchant_name.lower()
        
        # Get embedding for the transaction
        transaction_embedding = self.model.encode([text])[0]
        
        # Calculate similarity with each category
        similarities = {}
        for category, category_embedding in self.category_embeddings.items():
            similarity = cosine_similarity(
                transaction_embedding.reshape(1, -1),
                category_embedding.reshape(1, -1)
            )[0][0]
            similarities[category] = float(similarity)
        
        # Get the category with highest similarity
        best_category = max(similarities, key=similarities.get)
        confidence = similarities[best_category]
        
        return best_category, confidence
    
    def get_transaction_embedding(self, transaction_name: str, merchant_name: Optional[str] = None) -> List[float]:
        """Get embedding vector for a transaction"""
        text = transaction_name.lower()
        if merchant_name:
            text += " " + merchant_name.lower()
        embedding = self.model.encode([text])[0]
        return embedding.tolist()
    
    def classify_batch(self, transactions: List[Dict]) -> List[Tuple[str, float]]:
        """Classify multiple transactions at once"""
        results = []
        for transaction in transactions:
            category, confidence = self.classify_transaction(
                transaction.get("name", ""),
                transaction.get("merchant_name")
            )
            results.append((category, confidence))
        return results

# Global classifier instance
classifier = TransactionClassifier()

def get_classifier() -> TransactionClassifier:
    return classifier

