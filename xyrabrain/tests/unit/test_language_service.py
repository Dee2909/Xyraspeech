"""Unit tests for LanguageService."""

import pytest
from xyrabrain.app.models.enums import SupportedLanguage
from xyrabrain.app.services.language_service import language_service


def test_detect_pure_tamil():
    text = "வணக்கம்! நீங்கள் எப்படி இருக்கிறீர்கள்?"
    lang = language_service.detect_language(text)
    assert lang == SupportedLanguage.TAMIL


def test_detect_pure_english():
    text = "Hello! How are you doing today?"
    lang = language_service.detect_language(text)
    assert lang == SupportedLanguage.ENGLISH


def test_detect_mixed_code_switching():
    text = "Today meeting ரொம்ப important, please attend பண்ணுங்க."
    lang = language_service.detect_language(text)
    assert lang == SupportedLanguage.MIXED


def test_detect_numbers_and_punctuation():
    text = "123456 !!! ??? ..."
    lang = language_service.detect_language(text)
    assert lang == SupportedLanguage.ENGLISH


def test_validate_or_detect_explicit():
    assert language_service.validate_or_detect("வணக்கம்", "ta") == SupportedLanguage.TAMIL
    assert language_service.validate_or_detect("Hello there", "en") == SupportedLanguage.ENGLISH
    assert language_service.validate_or_detect("வணக்கம் Hello", "ta-en") == SupportedLanguage.MIXED


def test_validate_or_detect_unsupported_language_code():
    with pytest.raises(ValueError, match="Unsupported language 'fr'"):
        language_service.validate_or_detect("Bonjour", "fr")


def test_unsupported_foreign_script_rejection():
    # Devanagari Hindi text
    hindi_text = "नमस्ते, आप कैसे हैं? आज मौसम बहुत अच्छा है।"
    with pytest.raises(ValueError, match="Unsupported script detected"):
        language_service.detect_language(hindi_text)
