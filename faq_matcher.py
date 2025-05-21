
import difflib

class FAQMatcher:
    def __init__(self, faq_data):
        self.faqs = faq_data

    def find_best_match(self, user_query, threshold=0.6):
        best_score = 0
        best_answer = None
        for entry in self.faqs:
            score = difflib.SequenceMatcher(None, user_query.lower(), entry['answer'].lower()).ratio()
            if score > best_score:
                best_score = score
                best_answer = entry['answer']
        if best_score >= threshold:
            return {"response": best_answer, "confidence": "medium", "match_score": best_score}
        return {"response": "I'm not sure how to answer that. You may want to contact support.", "confidence": "low"}
