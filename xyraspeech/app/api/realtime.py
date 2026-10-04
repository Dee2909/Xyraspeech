"""Real-time Bidirectional WebSocket Audio Streaming Endpoint."""

import base64
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from xyraspeech.app.core.logging import logger
from xyraspeech.app.models.enums import WebSocketEventType
from xyraspeech.app.orchestration.orchestrator import orchestrator
from xyraspeech.app.schemas.events import WSInboundEvent

router = APIRouter(tags=["Real-Time Streaming"])


@router.websocket("/api/v1/voice/stream")
@router.websocket("/api/v1/conversation")
async def websocket_voice_stream(websocket: WebSocket):
    """Full-duplex real-time interactive voice streaming with barge-in interruption."""
    await websocket.accept()
    session = orchestrator.create_session(websocket=websocket)
    logger.info(f"[WS] Client connected. Session ID: {session.session_id}")

    await session.send_event(
        WebSocketEventType.SESSION_START,
        {
            "session_id": session.session_id,
            "message": "Connected to XyraSpeech real-time voice stream.",
        },
    )

    try:
        while True:
            # Handle text JSON frames or binary audio frames
            message = await websocket.receive()

            if "bytes" in message and message["bytes"]:
                # Binary audio chunk from client microphone
                raw_chunk = message["bytes"]
                session.audio_buffer.extend(raw_chunk)

            elif "text" in message and message["text"]:
                try:
                    payload = json.loads(message["text"])
                    event_type = payload.get("event")

                    if event_type == WebSocketEventType.INTERRUPT.value:
                        # Client sent explicit barge-in interrupt signal
                        await session.interrupt()

                    elif event_type == WebSocketEventType.AUDIO_CHUNK.value:
                        b64_audio = payload.get("audio_base64")
                        if b64_audio:
                            chunk = base64.b64decode(b64_audio)
                            session.audio_buffer.extend(chunk)

                    elif event_type == WebSocketEventType.SPEECH_END.value:
                        # Client indicates user finished speaking
                        await session.process_user_audio_buffer()

                    elif event_type == WebSocketEventType.SESSION_END.value:
                        break

                except json.JSONDecodeError:
                    pass

    except WebSocketDisconnect:
        logger.info(f"[WS] Client disconnected. Session ID: {session.session_id}")
    except Exception as exc:
        logger.warning(f"[WS] Exception in session {session.session_id}: {exc}")
    finally:
        await session.interrupt()
        orchestrator.remove_session(session.session_id)
