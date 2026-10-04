"""Dedicated contract verification for Tamil and English speech categories."""

import pytest
from unittest.mock import AsyncMock, patch
from xyrabrain.app.models.enums import Emotion, SpeakingStyle, SupportedLanguage
from xyrabrain.app.services.brain_service import brain_service


@pytest.mark.parametrize(
    "category,expected_emotion,expected_style",
    [
        ("neutral", Emotion.NEUTRAL, SpeakingStyle.CONVERSATIONAL),
        ("happy", Emotion.HAPPY, SpeakingStyle.ENTHUSIASTIC),
        ("question", Emotion.CURIOUS, SpeakingStyle.CONVERSATIONAL),
        ("sad", Emotion.SAD, SpeakingStyle.EMPATHETIC),
        ("formal", Emotion.SERIOUS, SpeakingStyle.PROFESSIONAL),
        ("conversational", Emotion.NEUTRAL, SpeakingStyle.FRIENDLY),
        ("mixed", Emotion.NEUTRAL, SpeakingStyle.CONVERSATIONAL),
    ],
)
def test_tamil_speech_categories(test_client, sample_tamil_sentences, category, expected_emotion, expected_style):
    tamil_text = sample_tamil_sentences[category]
    expected_lang = "ta-en" if category == "mixed" else "ta"

    mock_response = {
        "language": expected_lang,
        "speech_text": tamil_text,
        "overall_style": expected_style.value,
        "overall_emotion": expected_emotion.value,
        "segments": [
            {
                "text": tamil_text,
                "emotion": expected_emotion.value,
                "style": expected_style.value,
                "energy": 0.6 if expected_emotion in [Emotion.HAPPY, Emotion.EXCITED] else 0.5,
                "speed": 1.0,
                "pitch": 1.0,
                "emphasis": [],
                "pause_before_ms": 0,
                "pause_after_ms": 300,
            }
        ],
    }

    with patch.object(brain_service.client, "chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = mock_response

        response = test_client.post(
            "/api/v1/brain/express",
            json={"text": tamil_text},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == expected_lang
        assert data["speech_text"] == tamil_text
        assert data["overall_emotion"] == expected_emotion.value
        assert data["overall_style"] == expected_style.value
        assert len(data["segments"]) >= 1
        assert data["segments"][0]["text"] == tamil_text


def test_tamil_unicode_preservation(test_client):
    """Ensures Tamil Unicode glyphs and characters are 100% preserved."""
    pure_tamil = "வணக்கம், தங்களை அன்புடன் வரவேற்கிறோம்!"
    mock_response = {
        "language": "ta",
        "speech_text": pure_tamil,
        "overall_style": "friendly",
        "overall_emotion": "warm",
        "segments": [
            {
                "text": pure_tamil,
                "emotion": "warm",
                "style": "friendly",
                "energy": 0.55,
                "speed": 1.0,
                "pitch": 1.0,
                "emphasis": ["வரவேற்கிறோம்"],
                "pause_after_ms": 300,
            }
        ],
    }

    with patch.object(brain_service.client, "chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = mock_response

        response = test_client.post(
            "/api/v1/brain/express",
            json={"text": pure_tamil, "language": "ta"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["speech_text"] == pure_tamil
        assert "வரவேற்கிறோம்" in data["segments"][0]["emphasis"]
