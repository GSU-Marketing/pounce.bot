from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import json
from faq_matcher import FAQMatcher

KNOWN_FAQS = {
    "application deadline": "The application deadline is April 15.",
    "scholarship": "Scholarship information is available at /financial-aid.",
    "where do i apply": "You can apply at apply.university.edu.",
}

with open("faq_data.json") as f:
    matcher = FAQMatcher(json.load(f))

class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = None

class SlateStatusRequest(BaseModel):
    app_id: str

class SlateInquiryForm(BaseModel):
    first_name: str
    last_name: str
    email: str
    interest: str

app = FastAPI()

@app.post("/chat")
async def chat_response(data: ChatMessage):
    msg = data.message.lower()
    for keyword, answer in KNOWN_FAQS.items():
        if keyword in msg:
            return {"response": answer, "confidence": "high"}
    if "status" in msg and "application" in msg:
        return {"response": "Can you please provide your application ID?", "intent": "check_status", "confidence": "low"}
    return matcher.find_best_match(msg)

@app.get("/slate/status")
async def slate_status(app_id: str):
    return {"app_id": app_id, "status": "Under Review", "last_updated": "2025-04-01"}

@app.post("/slate/inquiry")
async def slate_inquiry(form: SlateInquiryForm):
    return {"message": "Your inquiry has been submitted.", "data_received": form.dict()}