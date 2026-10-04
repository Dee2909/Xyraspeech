from xyrabrain.app.api.brain import router as brain_router
from xyraspeech.app.api.conversation import router as conversation_router
from xyraspeech.app.api.health import router as health_router
from xyraspeech.app.api.realtime import router as realtime_router
from xyraspeech.app.api.stt import router as stt_router
from xyraspeech.app.api.translate import router as translate_router
from xyraspeech.app.api.tts import router as tts_router
from xyraspeech.app.api.voices import router as voices_router

__all__ = [
    "brain_router",
    "conversation_router",
    "health_router",
    "realtime_router",
    "stt_router",
    "translate_router",
    "tts_router",
    "voices_router",
]
