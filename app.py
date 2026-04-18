"""
FastAPI entrypoint for IDEAL AI College Assistant.
Run locally: uvicorn app:app --reload
"""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from core.router import route_message
from services.college_service import get_college_summary
from services.media_service import get_college_images, get_college_video
from services.news_service import fetch_news

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger("ideal-ai.api")

app = FastAPI(title="IDEAL AI College Assistant", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class ChatRequest(BaseModel):
    message: str = Field(default="")
    conversationHistory: list[dict[str, Any]] = Field(default_factory=list)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/chat")
@app.post("/assistant-api/chat")
async def chat(payload: ChatRequest) -> dict[str, Any]:
    message = payload.message.strip()
    if not message:
        return JSONResponse({"error": "Message is required"}, status_code=400)

    history = payload.conversationHistory if isinstance(payload.conversationHistory, list) else []
    try:
        response = route_message(message, history)
        if not isinstance(response, dict):
            raise ValueError("Invalid router response")
        return response
    except Exception:
        logger.exception("Unhandled chat error")
        return JSONResponse(
            {
                "reply": "Sorry, something went wrong. Please try again.",
                "intent": "general",
                "show_images": False,
                "images": [],
                "show_video": False,
                "video_url": None,
            },
            status_code=500,
        )


@app.get("/api/college-info")
@app.get("/assistant-api/college-info")
async def college_info() -> dict[str, Any]:
    return get_college_summary()


@app.get("/api/news")
@app.get("/assistant-api/news")
async def news(query: str | None = None) -> dict[str, Any]:
    try:
        return {"articles": fetch_news(query)}
    except Exception:
        logger.exception("Unhandled error in news endpoint")
        return {"articles": []}


@app.get("/api/media/images")
@app.get("/assistant-api/media/images")
async def media_images() -> list[str]:
    return get_college_images()


@app.get("/api/media/video")
@app.get("/assistant-api/media/video")
async def media_video() -> str:
    return get_college_video()


@app.get("/api/healthz")
@app.get("/assistant-api/healthz")
async def health() -> dict[str, str]:
    return {"status": "ok"}