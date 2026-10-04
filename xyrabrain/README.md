# XyraBrain — Ollama-Powered Speech Intelligence Engine

> **The intelligence layer for XyraSpeech**, generating fine-grained speech performance instructions, emotion directions, segmentation, and prosody parameters for downstream TTS engines.

---

## 1. What is XyraBrain?

**XyraBrain is NOT a TTS engine.** It does not generate audio.

XyraBrain is the **language and delivery intelligence engine** that analyzes input text and determines:
- What should be spoken (`speech_text`)
- Language detection and preservation (`ta` Tamil, `en` English, `ta-en` Mixed code-switching)
- Logical speech segments and sentence boundaries
- Granular emotion (`happy`, `excited`, `warm`, `curious`, `sad`, `serious`, etc.)
- Overall speaking style (`conversational`, `enthusiastic`, `professional`, etc.)
- Dynamic energy levels (`0.0` to `1.0`), speech rate / speed (`0.5` to `1.5`), and pitch modifier (`0.8` to `1.2`)
- Word-level emphasis and pause duration (`pause_before_ms`, `pause_after_ms`)
- Punctuation and flow enhancements

The resulting **SpeechDirection** JSON object is passed to downstream TTS adapters (such as AI4Bharat Indic-TTS, OpenVoice, or OS-native synthesizers).

---

## 2. Architecture

```
User / Application Request
           │
           ▼
┌──────────────────────────────────────┐
│             XyraBrain                │
│  FastAPI + Pydantic Validation       │
│  Ollama Language Intelligence Model  │
└──────────────────┬───────────────────┘
                   │ SpeechDirection JSON
                   ▼
┌──────────────────────────────────────┐
│        Expression Adapter            │
│  Capability Filtering & SSML builder │
└──────────────────┬───────────────────┘
                   │ Engine-neutral TTSInstructions
                   ▼
┌──────────────────────────────────────┐
│            TTS Engine                │
│  (AI4Bharat Indic-TTS / OpenVoice)   │
└──────────────────┬───────────────────┘
                   │
                   ▼
              Audio Waveform
```

> **Key Rule**: *XyraBrain determines expression; the downstream TTS engine determines how much of that expression can actually be rendered based on its supported capabilities.*

---

## 3. Core Processing Modes

1. **RAW (`/api/v1/brain/analyze` with `mode="raw"`)**:
   - Bypasses Ollama entirely.
   - Preserves exact input text without modifying single characters or spaces.
   - Produces sentence-segmented SpeechDirection with neutral default delivery.
2. **ENHANCED (`/api/v1/brain/enhance`)**:
   - Calls Ollama to improve punctuation, capitalization, and sentence boundaries for spoken flow.
   - Strictly forbids altering core meaning, translating, or adding unrequested content.
3. **EXPRESSIVE (`/api/v1/brain/express`)**:
   - Full cognitive speech analysis generating emotion, style, emphasis, and pitch/speed/pause instructions.
   - Enforces automated text-preservation verification against unintended translation or hallucination.

---

## 4. Supported Languages

* **Tamil (`ta`)**: Preserves Tamil Unicode script, handles conversational vs. formal Tamil, and preserves emotional intent without Romanization or translation.
* **English (`en`)**: Handles standard spoken English.
* **Tamil-English Mixed (`ta-en`)**: Experimental support for natural code-switching (e.g., *"Today meeting ரொம்ப important"*).

---

## 5. Quickstart & Installation

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) installed locally

### Step 1: Clone and Set Up Virtual Environment
```bash
git clone <repo_url>
cd xyrabrain

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
cp .env.example .env
```

Default `.env` settings:
```ini
APP_NAME=XyraBrain
APP_VERSION=0.1.0
HOST=127.0.0.1
PORT=8000
DEBUG=false

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral:latest
OLLAMA_TIMEOUT=90

MAX_TEXT_LENGTH=12000
MAX_SEGMENTS=50
MAX_RETRIES=2
```

### Step 3: Start Ollama and Pull a Model
```bash
# In a separate terminal or service
ollama serve

# Pull your preferred local model (e.g., mistral or llama3.2:3b)
ollama pull mistral:latest
```

### Step 4: Run Diagnostic Check & Smoke Test
```bash
# Verify Ollama reachability and model status
python scripts/check_ollama.py

# Run full end-to-end smoke test
python scripts/smoke_test.py
```

### Step 5: Start the API Server
```bash
uvicorn xyrabrain.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive OpenAPI Swagger UI is available at: `http://127.0.0.1:8000/docs`

---

## 6. API Examples

### 1. Health Checks
```bash
curl -X GET http://127.0.0.1:8000/health
curl -X GET http://127.0.0.1:8000/health/ollama
```

### 2. Expressive Analysis (English)
```bash
curl -X POST http://127.0.0.1:8000/api/v1/brain/express \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Wow! You actually did it! I am really proud of you!",
    "language": "en"
  }'
```

**Example Response:**
```json
{
  "language": "en",
  "speech_text": "Wow! You actually did it! I am really proud of you!",
  "overall_style": "enthusiastic",
  "overall_emotion": "excited",
  "segments": [
    {
      "text": "Wow!",
      "emotion": "surprised",
      "style": "enthusiastic",
      "energy": 0.9,
      "speed": 1.1,
      "pitch": 1.05,
      "emphasis": ["Wow"],
      "pause_before_ms": 0,
      "pause_after_ms": 300,
      "pronunciation_hint": null
    },
    {
      "text": "You actually did it!",
      "emotion": "excited",
      "style": "enthusiastic",
      "energy": 0.9,
      "speed": 1.08,
      "pitch": 1.02,
      "emphasis": ["actually", "did it"],
      "pause_before_ms": 0,
      "pause_after_ms": 350,
      "pronunciation_hint": null
    },
    {
      "text": "I am really proud of you!",
      "emotion": "warm",
      "style": "friendly",
      "energy": 0.75,
      "speed": 0.95,
      "pitch": 0.98,
      "emphasis": ["really proud"],
      "pause_before_ms": 0,
      "pause_after_ms": 0,
      "pronunciation_hint": null
    }
  ],
  "metadata": {
    "model": "ollama:mistral:latest",
    "processing_mode": "expressive",
    "generated_at": "2026-10-04T08:30:00Z",
    "processing_time_ms": 142.5,
    "schema_version": "1.0",
    "retry_count": 0
  }
}
```

### 3. Expressive Analysis (Tamil)
```bash
curl -X POST http://127.0.0.1:8000/api/v1/brain/express \
  -H "Content-Type: application/json" \
  -d '{
    "text": "அருமை! நீ உண்மையிலேயே அதை செய்துவிட்டாய்!",
    "language": "ta"
  }'
```

---

## 7. Testing Suite

Run all automated unit and API test suites:
```bash
pytest
```

---

## 8. Downstream Expression Adapter Integration

To connect XyraBrain with a custom TTS engine:

```python
from xyrabrain.app.models.enums import TTSCapability
from xyrabrain.app.services.expression_adapter import BaseTTSAdapter, TTSInstruction

class MyCustomTTSAdapter(BaseTTSAdapter):
    def __init__(self):
        super().__init__(
            name="MyCustomTTSAdapter",
            capabilities={
                TTSCapability.SUPPORTS_SPEED,
                TTSCapability.SUPPORTS_PITCH,
                TTSCapability.SUPPORTS_PAUSE,
            }
        )

    async def synthesize(self, instruction: TTSInstruction) -> bytes:
        # instruction.speed and instruction.pitch are populated
        # unsupported instruction.emotion is stripped safely from the engine payload
        return await call_underlying_tts_engine(instruction)
```

---

## 9. Known Limitations

1. **Hardware Constraints**: Local LLM inference speed depends on Apple Silicon / GPU memory. On constrained machines, consider using smaller quantized models (e.g., `llama3.2:3b` or `qwen2.5:3b`).
2. **TTS Fidelity**: High energy/emotion metadata output from XyraBrain will only affect final speech if the connected TTS engine supports emotion embeddings or SSML prosody.
