"""Interactive Conversation API Endpoint."""

from fastapi import APIRouter, HTTPException, status
from xyraspeech.app.orchestration.orchestrator import orchestrator
from xyraspeech.app.schemas.conversation import (
    ConversationMessageRequest,
    ConversationMessageResponse,
)

router = APIRouter(prefix="/api/v1", tags=["Conversation"])


@router.post("/conversation/message", response_model=ConversationMessageResponse)
async def process_conversation_message(request: ConversationMessageRequest) -> ConversationMessageResponse:
    """Processes a conversational turn with memory context and generates real speech."""
    if not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "EMPTY_MESSAGE", "message": "Message text cannot be empty."},
        )

    try:
        return await orchestrator.process_text_message(
            text=request.text,
            conversation_id=request.conversation_id,
            language=request.language,
            voice_id=request.voice_id,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "CONVERSATION_ERROR", "message": str(exc)},
        )
