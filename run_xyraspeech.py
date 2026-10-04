#!/usr/bin/env python3
"""Runner script for XyraSpeech Production Platform."""

import sys
import uvicorn
from xyraspeech.app.core.config import settings

if __name__ == "__main__":
    print(f"🚀 Launching {settings.APP_NAME} Production Gateway on http://{settings.HOST}:{settings.PORT}")
    uvicorn.run("xyraspeech.app.main:app", host=settings.HOST, port=settings.PORT, reload=False)
