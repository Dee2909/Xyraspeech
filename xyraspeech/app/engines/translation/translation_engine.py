"""Real Local Translation Engine for Tamil <-> English."""

import time
from typing import Optional
from xyrabrain.app.services.ollama_client import ollama_client
from xyraspeech.app.core.logging import log_event, logger
from xyraspeech.app.schemas.translation import TranslationResponse


class TranslationEngine:
    """Translation engine handling Tamil <-> English translation."""

    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> TranslationResponse:
        """Translates text between Tamil and English."""
        start_time = time.perf_counter()

        src = source_language.lower()
        tgt = target_language.lower()

        if src not in ["ta", "en"] or tgt not in ["ta", "en"]:
            raise ValueError(f"Unsupported translation pair '{src}' -> '{tgt}'. Only Tamil and English are supported.")

        if src == tgt:
            return TranslationResponse(
                source_text=text,
                translated_text=text,
                source_language=src,
                target_language=tgt,
                model="passthrough:identity",
            )

        src_name = "Tamil" if src == "ta" else "English"
        tgt_name = "Tamil" if tgt == "ta" else "English"

        system_prompt = (
            f"You are a professional translator translating from {src_name} to {tgt_name}.\n"
            f"CRITICAL RULES:\n"
            f"1. Translate the user input accurately while preserving tone, meaning, names, and numbers.\n"
            f"2. Output ONLY the translated text without any explanation, prefix, quotes, or notes.\n"
            f"3. If translating to Tamil, use proper Tamil script.\n"
            f"4. If translating to English, use natural conversational English."
        )

        user_prompt = f"Translate the following text from {src_name} to {tgt_name}:\n\n{text}"

        response = await ollama_client.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_format=False,
        )

        translated = ""
        if isinstance(response, dict):
            # In case Ollama returned raw message content
            translated = response.get("response", response.get("message", {}).get("content", str(response)))
        else:
            translated = str(response)

        translated = translated.strip().strip('"')

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        log_event(
            event="translation_completed",
            stage="translation",
            language=f"{src}->{tgt}",
            latency_ms=elapsed_ms,
            status="SUCCESS",
        )

        return TranslationResponse(
            source_text=text,
            translated_text=translated,
            source_language=src,
            target_language=tgt,
            model=f"ollama:{ollama_client.model}",
        )


translation_engine = TranslationEngine()
