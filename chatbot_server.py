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

from fastapi.responses import HTMLResponse

@app.get("/bot.js")
async def serve_widget_script():
    js_code = '''
    window.onload = function () {
      var frame = document.createElement("iframe");
      frame.src = "https://pounce-bot.vercel.app";
      frame.style = "width: 350px; height: 500px; position: fixed; bottom: 10px; right: 10px; border: none; z-index: 9999;";
      frame.setAttribute("aria-label", "GSU Chatbot");
      document.body.appendChild(frame);
    };
    '''
    return HTMLResponse(content=js_code, media_type="application/javascript")


@app.post("/chat")
async def chat_response(data: ChatMessage):
    msg = data.message.lower()
    for keyword, answer in KNOWN_FAQS.items():
        if keyword in msg:
            return {"response": answer, "confidence": "high"}
    if "status" in msg and "application" in msg:
        return {"response": "Can you please provide your application ID?", "intent": "check_status", "confidence": "low"}
    return matcher.find_best_match(msg)

import httpx  # Add at the top with other imports

SLATE_URL = (
    "https://gradapply.gsu.edu/manage/query/run"
    "?id=51c80ecd-39f2-40c2-bdca-16eda904efd6"
    "&cmd=service&output=json"
)

@app.get("/slate/status")
async def slate_status(
    panther_id: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    phone: Optional[str] = None,
    birthdate: Optional[str] = None,
    email: Optional[str] = None,
):
    # Only include fields that are filled in
    provided = {k: v for k, v in {
        "panther_id": panther_id,
        "first_name": first_name,
        "last_name": last_name,
        "phone": phone,
        "birthdate": birthdate,
        "email": email,
    }.items() if v}

    if len(provided) < 3:
        return {
            "status": "error",
            "message": "Please provide at least 3 pieces of information (e.g. Panther ID, First Name, Birthdate)."
        }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(SLATE_URL, params=provided)
            response.raise_for_status()
            data = response.json()
        return {"status": "success", "results": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}



@app.post("/slate/inquiry")
async def slate_inquiry(form: SlateInquiryForm):
    return {"message": "Your inquiry has been submitted.", "data_received": form.dict()}
