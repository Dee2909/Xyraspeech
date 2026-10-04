"""Unit tests for ValidationService."""

import pytest
from xyrabrain.app.models.enums import Emotion, SpeakingStyle, SupportedLanguage
from xyrabrain.app.services.validation_service import (
    TextPreservationError,
    validation_service,
)


def test_numeric_clamping():
    assert validation_service.clamp_numeric(2.5, 0.5, 1.5, 1.0) == 1.5
    assert validation_service.clamp_numeric(0.1, 0.5, 1.5, 1.0) == 0.5
    assert validation_service.clamp_numeric(1.2, 0.5, 1.5, 1.0) == 1.2
    assert validation_service.clamp_numeric("invalid", 0.5, 1.5, 1.0) == 1.0


def test_int_clamping():
    assert validation_service.clamp_int(5000, 0, 3000, 0) == 3000
    assert validation_service.clamp_int(-100, 0, 3000, 0) == 0
    assert validation_service.clamp_int(450, 0, 3000, 0) == 450


def test_emotion_normalization():
    assert validation_service.normalize_emotion("excited") == Emotion.EXCITED
    assert validation_service.normalize_emotion("HAPPY") == Emotion.HAPPY
    assert validation_service.normalize_emotion("super_joyful_fantasy") == Emotion.NEUTRAL
    assert validation_service.normalize_emotion(None) == Emotion.NEUTRAL


def test_style_normalization():
    assert validation_service.normalize_style("friendly") == SpeakingStyle.FRIENDLY
    assert validation_service.normalize_style("PROFESSIONAL") == SpeakingStyle.PROFESSIONAL
    assert validation_service.normalize_style("unknown_style") == SpeakingStyle.NEUTRAL
    assert validation_service.normalize_style(None) == SpeakingStyle.NEUTRAL


def test_normalize_segment():
    raw = {
        "text": "Hello world",
        "emotion": "excited",
        "style": "conversational",
        "energy": 1.8,  # Should clamp to 1.0
        "speed": 0.2,   # Should clamp to 0.5
        "pitch": 1.4,   # Should clamp to 1.2
        "pause_after_ms": 4000,  # Should clamp to 3000
        "emphasis": ["one", "two", "three", "four"],  # Should truncate to 3
    }
    seg = validation_service.normalize_segment(raw)
    assert seg.energy == 1.0
    assert seg.speed == 0.5
    assert seg.pitch == 1.2
    assert seg.pause_after_ms == 3000
    assert len(seg.emphasis) == 3


def test_text_preservation_translation_detection():
    tamil_orig = "வணக்கம் நண்பா!"
    english_translation = "Hello friend!"

    # Should raise error when Tamil original is turned into English speech_text
    with pytest.raises(TextPreservationError, match="Translation detected"):
        validation_service.verify_text_preservation(
            original_text=tamil_orig,
            speech_text=english_translation,
            expected_lang=SupportedLanguage.TAMIL,
        )


def test_text_preservation_missing_numbers():
    orig = "The OTP code is 987456 and it expires in 5 minutes."
    bad_speech = "The OTP code is and it expires in 5 minutes."

    with pytest.raises(TextPreservationError, match="Number preservation failure"):
        validation_service.verify_text_preservation(
            original_text=orig,
            speech_text=bad_speech,
            expected_lang=SupportedLanguage.ENGLISH,
        )


def test_text_preservation_severe_truncation():
    orig = "This is a very long text with many critical details that shouldn't disappear."
    bad_speech = "Short."

    with pytest.raises(TextPreservationError, match="Severe text truncation"):
        validation_service.verify_text_preservation(
            original_text=orig,
            speech_text=bad_speech,
            expected_lang=SupportedLanguage.ENGLISH,
        )
