#!/usr/bin/env python3
"""End-to-end smoke test for XyraBrain."""

import asyncio
import json
import sys
import time
from pathlib import Path

# Ensure root package is in pythonpath
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from xyrabrain.app.core.config import settings
from xyrabrain.app.models.enums import ProcessingMode, SupportedLanguage
from xyrabrain.app.services.brain_service import brain_service
from xyrabrain.app.services.expression_adapter import IndicTTSAdapter, OpenVoiceAdapter
from xyrabrain.app.services.ollama_client import ollama_client


async def run_smoke_test():
    print("=" * 70)
    print("🚀 RUNNING XYRABRAIN COMPREHENSIVE SMOKE TEST")
    print(f"Model: {settings.OLLAMA_MODEL} | Base URL: {settings.OLLAMA_BASE_URL}")
    print("=" * 70)

    steps_passed = 0
    total_steps = 6

    # 1. Ollama Reachable Check
    print("\n[Step 1/6] Verifying Ollama server reachability...")
    health = await ollama_client.check_health()
    if health.get("reachable"):
        print("  [PASS] Ollama reachable at", settings.OLLAMA_BASE_URL)
        steps_passed += 1
    else:
        print("  [FAIL] Ollama unreachable:", health.get("error"))
        print("\nSmoke test aborted. Please start Ollama before running live tests.")
        await ollama_client.close()
        return

    # 2. Model Availability Check
    print(f"\n[Step 2/6] Checking availability of model '{settings.OLLAMA_MODEL}'...")
    if health.get("model_available"):
        print(f"  [PASS] Model '{settings.OLLAMA_MODEL}' is ready.")
        steps_passed += 1
    else:
        print(f"  [FAIL] Model '{settings.OLLAMA_MODEL}' not found. Available: {health.get('installed_models')}")
        print(f"  Run: 'ollama pull {settings.OLLAMA_MODEL}'")
        await ollama_client.close()
        return

    # 3. English Expressive Analysis
    print("\n[Step 3/6] Testing English Expressive Speech Direction...")
    en_sample = "Wow! You actually did it! I'm really proud of you!"
    start_en = time.perf_counter()
    try:
        en_direction = await brain_service.process(
            text=en_sample,
            language=SupportedLanguage.ENGLISH,
            mode=ProcessingMode.EXPRESSIVE,
        )
        elapsed_en = (time.perf_counter() - start_en) * 1000.0
        print(f"  [PASS] English analysis completed in {elapsed_en:.1f}ms")
        print(f"         Detected Emotion: {en_direction.overall_emotion.value}")
        print(f"         Detected Style:   {en_direction.overall_style.value}")
        print(f"         Segments Count:   {len(en_direction.segments)}")
        for i, s in enumerate(en_direction.segments, 1):
            print(f"           - Seg {i}: \"{s.text}\" | Emotion: {s.emotion.value} | Energy: {s.energy:.2f} | Speed: {s.speed:.2f}")
        steps_passed += 1
    except Exception as exc:
        print("  [FAIL] English analysis error:", str(exc))
        en_direction = None

    # 4. Tamil Expressive Analysis
    print("\n[Step 4/6] Testing Tamil Expressive Speech Direction...")
    ta_sample = "அருமை! நீ உண்மையிலேயே அதை செய்துவிட்டாய்! எனக்கு ரொம்ப பெருமையா இருக்கு!"
    start_ta = time.perf_counter()
    try:
        ta_direction = await brain_service.process(
            text=ta_sample,
            language=SupportedLanguage.TAMIL,
            mode=ProcessingMode.EXPRESSIVE,
        )
        elapsed_ta = (time.perf_counter() - start_ta) * 1000.0
        print(f"  [PASS] Tamil analysis completed in {elapsed_ta:.1f}ms")
        print(f"         Detected Emotion: {ta_direction.overall_emotion.value}")
        print(f"         Detected Style:   {ta_direction.overall_style.value}")
        print(f"         Segments Count:   {len(ta_direction.segments)}")
        for i, s in enumerate(ta_direction.segments, 1):
            print(f"           - Seg {i}: \"{s.text}\" | Emotion: {s.emotion.value} | Energy: {s.energy:.2f} | Speed: {s.speed:.2f}")
        steps_passed += 1
    except Exception as exc:
        print("  [FAIL] Tamil analysis error:", str(exc))
        ta_direction = None

    # 5. Schema Validation & Numeric Clamping Check
    print("\n[Step 5/6] Validating schema integrity and range clamping...")
    if en_direction and ta_direction:
        assert en_direction.language == SupportedLanguage.ENGLISH
        assert ta_direction.language == SupportedLanguage.TAMIL
        for seg in en_direction.segments + ta_direction.segments:
            assert settings.MIN_ENERGY <= seg.energy <= settings.MAX_ENERGY
            assert settings.MIN_SPEED <= seg.speed <= settings.MAX_SPEED
            assert settings.MIN_PITCH <= seg.pitch <= settings.MAX_PITCH
            assert settings.MIN_PAUSE_MS <= seg.pause_before_ms <= settings.MAX_PAUSE_MS
            assert settings.MIN_PAUSE_MS <= seg.pause_after_ms <= settings.MAX_PAUSE_MS
            assert len(seg.emphasis) <= settings.MAX_EMPHASIS_PER_SEGMENT
        print("  [PASS] All segments strictly adhere to Pydantic constraints and numeric bounds.")
        steps_passed += 1
    else:
        print("  [FAIL] Schema check skipped due to upstream failure.")

    # 6. Expression Adapter & TTS Dispatch Testing
    print("\n[Step 6/6] Testing downstream Expression Adapters...")
    if en_direction:
        indic_adapter = IndicTTSAdapter()
        openvoice_adapter = OpenVoiceAdapter()

        indic_result = indic_adapter.adapt(en_direction)
        openvoice_result = openvoice_adapter.adapt(en_direction)

        print(f"  [PASS] IndicTTSAdapter dispatched {len(indic_result.instructions)} instructions.")
        print(f"         Applied capabilities: {indic_result.applied_capabilities}")
        print(f"         Dropped capabilities: {indic_result.dropped_capabilities}")
        print(f"  [PASS] OpenVoiceAdapter dispatched {len(openvoice_result.instructions)} instructions.")
        print(f"         Applied capabilities: {openvoice_result.applied_capabilities}")
        print(f"         Dropped capabilities: {openvoice_result.dropped_capabilities}")
        steps_passed += 1
    else:
        print("  [FAIL] Adapter check skipped.")

    await ollama_client.close()

    print("\n" + "=" * 70)
    print(f"SMOKE TEST SUMMARY: {steps_passed}/{total_steps} Passed")
    print("=" * 70)

    if steps_passed == total_steps:
        print("🎉 ALL SMOKE TESTS COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("⚠️ SOME SMOKE TESTS FAILED OR SKIPPED.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_smoke_test())
