"""Tests for WebSocket Real-Time Voice Streaming and Interruption."""

import base64
from fastapi.testclient import TestClient
from xyraspeech.app.models.enums import WebSocketEventType


def test_websocket_session_lifecycle(test_client, sample_wav_bytes):
    with test_client.websocket_connect("/api/v1/voice/stream") as ws:
        # 1. Receive session_start event
        start_event = ws.receive_json()
        assert start_event["event"] == WebSocketEventType.SESSION_START.value
        session_id = start_event["session_id"]
        assert session_id is not None

        # 2. Send audio chunk
        b64_data = base64.b64encode(sample_wav_bytes).decode("utf-8")
        ws.send_json({
            "event": WebSocketEventType.AUDIO_CHUNK.value,
            "audio_base64": b64_data,
        })

        # 3. Send interruption / barge-in event
        ws.send_json({
            "event": WebSocketEventType.INTERRUPT.value,
        })
        interrupt_event = ws.receive_json()
        assert interrupt_event["event"] == WebSocketEventType.INTERRUPT.value
        assert interrupt_event["data"]["status"] == "speech_interrupted"
