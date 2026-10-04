#!/usr/bin/env python3
"""Diagnostic script to check local Ollama installation and model readiness."""

import asyncio
import sys
from pathlib import Path

# Ensure root package is in pythonpath
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from xyrabrain.app.core.config import settings
from xyrabrain.app.services.ollama_client import ollama_client


async def main():
    print("=" * 60)
    print(f"XyraBrain Ollama Health Check ({settings.APP_NAME})")
    print("=" * 60)
    print(f"Target Base URL:     {settings.OLLAMA_BASE_URL}")
    print(f"Configured Model:    {settings.OLLAMA_MODEL}")
    print(f"Inference Timeout:   {settings.OLLAMA_TIMEOUT}s")
    print("-" * 60)

    result = await ollama_client.check_health()
    await ollama_client.close()

    if result.get("reachable"):
        print("[PASS] Ollama server is REACHABLE")
        print(f"Found {len(result.get('installed_models', []))} installed models:")
        for m in result.get("installed_models", []):
            is_active = "(ACTIVE)" if m == settings.OLLAMA_MODEL else ""
            print(f"  - {m} {is_active}")

        if result.get("model_available"):
            print(f"\n[PASS] Configured model '{settings.OLLAMA_MODEL}' is READY for inference.")
            sys.exit(0)
        else:
            print(f"\n[FAIL] Configured model '{settings.OLLAMA_MODEL}' is NOT found in installed models.")
            print(f"Please install it using:\n  ollama pull {settings.OLLAMA_MODEL}")
            sys.exit(1)
    else:
        print("[FAIL] Ollama server is NOT REACHABLE")
        print(f"Error details: {result.get('error')}")
        print("\nPlease ensure Ollama is running:\n  brew services start ollama  OR  ollama serve")
        sys.exit(2)


if __name__ == "__main__":
    asyncio.run(main())
