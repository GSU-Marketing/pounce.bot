from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import json
import httpx
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

import httpx  # Ensure this is imported at the top of the file

from fastapi import Query  # Make sure this is imported at the top if not already

SLATE_URL = "https://gradapply.gsu.edu/manage/service/api/gradtestbot/application_status"
SLATE_AUTH_HEADER = {
    "Authorization": "Bearer 1e5b8e64-548b-4341-843a-9a9bbbef92da"
}

@app.get("/slate/status")
async def slate_status(
    panther_id: Optional[str] = Query(None),
    first_name: Optional[str] = Query(None),
    last_name: Optional[str] = Query(None),
    phone: Optional[str] = Query(None),
    birthdate: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
):
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
            res = await client.get(SLATE_URL, params=provided, headers=SLATE_AUTH_HEADER)
            res.raise_for_status()
            slate_data = res.json()

        if not slate_data:
            return {"status": "error", "message": "No matching applications found."}

        formatted = []
        for app in slate_data:
            formatted.append({
                "Reference ID": app.get("ApplicationReferenceId", "N/A"),
                "Status": app.get("ApplicationStatus", "N/A"),
                "Program": app.get("AppliedProgram", "N/A"),
                "College": app.get("AppliedCollege", "N/A"),
                "Term": app.get("AppliedTerm", "N/A")
            })

        return {"status": "success", "results": formatted}

    except httpx.HTTPStatusError as e:
        return {"status": "error", "message": f"HTTP error: {e.response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}






@app.post("/slate/inquiry")
async def slate_inquiry(form: SlateInquiryForm):
    return {"message": "Your inquiry has been submitted.", "data_received": form.dict()}
