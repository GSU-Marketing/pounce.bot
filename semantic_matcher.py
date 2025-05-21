
from sentence_transformers import SentenceTransformer, util
import numpy as np

class SemanticMatcher:
    def __init__(self, faq_data, model_name='all-MiniLM-L6-v2'):
        self.faqs = faq_data
        self.model = SentenceTransformer(model_name)
        self.answers = [entry['answer'] for entry in faq_data]
        self.embeddings = self.model.encode(self.answers, convert_to_tensor=True)

    def find_best_match(self, query, threshold=0.6):
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        scores = util.cos_sim(query_embedding, self.embeddings)[0]
        best_score = float(scores.max())
        best_idx = int(scores.argmax())

        if best_score >= threshold:
            return {
                "response": self.answers[best_idx],
                "confidence": "high" if best_score > 0.75 else "medium",
                "match_score": best_score
            }
        else:
            return {
                "response": "I'm not sure how to answer that. Please contact support.",
                "confidence": "low",
                "match_score": best_score
            }
