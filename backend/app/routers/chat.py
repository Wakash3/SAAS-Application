from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import json
from groq import Groq
from ..core.database import get_db
from ..core.tenant import get_current_tenant
from ..core.config import settings
from ..core.security import rate_limit
from ..services.gladwell_service import gladwell_service

router = APIRouter(prefix="/chat", tags=["chat"])

# Groq client (initialized once)
groq_client = Groq(api_key=settings.GROQ_API_KEY)


class ChatRequest(BaseModel):
    message: str
    page_context: str
    branch_id: Optional[str] = None
    conversation_history: Optional[list] = []


@router.post("/message/stream")
async def chat_stream(
    payload: ChatRequest,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
):
    await rate_limit(request, limit=30, window=60)

    system = gladwell_service.build_prompt(
        payload.page_context, tenant_id, payload.branch_id, db
    )
    messages = payload.conversation_history + [
        {"role": "user", "content": payload.message}
    ]

    async def generate():
        try:
            # Create streaming completion
            stream = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",   # fast + capable model on Groq
                messages=[{"role": "system", "content": system}] + messages,
                max_tokens=600,
                temperature=0.3,
                stream=True,
            )
            
            # Iterate through the stream
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        text = delta.content
                        if text:
                            yield f"data: {json.dumps({'text': text})}\n\n"
                            
        except Exception as e:
            error_message = f"Gladwell error: {str(e)}"
            yield f"data: {json.dumps({'text': error_message})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")