"""Voice Cloning API Endpoints."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, Response, UploadFile, status
from pydantic import BaseModel, Field

from xyraspeech.app.core.security import verify_api_key
from xyraspeech.app.engines.cloning.voice_cloner import SpeakerProfile, voice_cloning_engine

router = APIRouter(tags=["Voice Cloning"])


class ClonedProfileResponse(BaseModel):
    voice_id: str
    name: str
    gender: str
    f0_mean_hz: float
    pitch_factor: float
    sample_rate: int = 24000
    status: str = "ready"


@router.post("/api/v1/voices/clone", response_model=ClonedProfileResponse)
@router.post("/v1/voices/add")
async def create_cloned_voice(
    name: str = Form(..., description="Name for the cloned voice (e.g. 'My Voice', 'Karthik')"),
    file: Optional[UploadFile] = File(default=None, description="Reference audio file (WAV, MP3, M4A)"),
    files: Optional[List[UploadFile]] = File(default=None, description="ElevenLabs format audio files list"),
    xi_api_key: Optional[str] = Header(default=None, alias="xi-api-key"),
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    authorization: Optional[str] = Header(default=None),
) -> Any:
    """Clones a speaker's vocal characteristics from an uploaded reference voice audio file."""
    await verify_api_key(x_api_key=xi_api_key or x_api_key, authorization=authorization)

    target_file = file
    if not target_file and files and len(files) > 0:
        target_file = files[0]

    if not target_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "MISSING_AUDIO_FILE", "message": "Please upload a reference audio file."},
        )

    try:
        audio_bytes = await target_file.read()
        if len(audio_bytes) < 1000:
            raise ValueError("Audio file is empty or corrupted.")

        profile = voice_cloning_engine.analyze_reference_audio(
            audio_bytes=audio_bytes,
            voice_name=name.strip(),
        )

        return {
            "voice_id": profile.voice_id,
            "name": profile.name,
            "gender": profile.gender,
            "f0_mean_hz": round(profile.f0_mean, 1),
            "pitch_factor": profile.pitch_factor,
            "sample_rate": 24000,
            "status": "ready",
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "VOICE_CLONING_ERROR", "message": str(exc)},
        )


@router.post("/api/v1/tts/clone")
async def synthesize_with_audio_reference(
    text: str = Form(..., min_length=1, description="Text to speak in cloned voice"),
    reference_audio: UploadFile = File(..., description="Reference speaker audio (WAV/MP3)"),
    voice_name: Optional[str] = Form(default="Temporary Clone"),
    language: Optional[str] = Form(default=None, description="Optional language: ta or en"),
    speed: float = Form(default=1.0),
    pitch: float = Form(default=1.0),
    emotion: str = Form(default="warm"),
    xi_api_key: Optional[str] = Header(default=None, alias="xi-api-key"),
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    authorization: Optional[str] = Header(default=None),
) -> Response:
    """Zero-shot instant synthesis: Upload reference audio + text and immediately receive cloned voice audio."""
    await verify_api_key(x_api_key=xi_api_key or x_api_key, authorization=authorization)

    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "EMPTY_TEXT", "message": "Text payload cannot be empty."},
        )

    try:
        ref_bytes = await reference_audio.read()
        profile = voice_cloning_engine.analyze_reference_audio(
            audio_bytes=ref_bytes,
            voice_name=voice_name,
        )

        cloned_wav = await voice_cloning_engine.synthesize_cloned(
            text=text.strip(),
            profile=profile,
            language=language,
            speed=speed,
            pitch=pitch,
            emotion=emotion,
        )

        return Response(
            content=cloned_wav,
            media_type="audio/wav",
            headers={
                "Content-Disposition": 'inline; filename="cloned_speech.wav"',
                "X-Voice-Id": profile.voice_id,
                "X-Gender": profile.gender,
                "X-Sample-Rate": "24000",
            },
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "CLONED_SYNTHESIS_ERROR", "message": str(exc)},
        )


@router.get("/api/v1/voices/cloned")
async def list_cloned_voices(
    xi_api_key: Optional[str] = Header(default=None, alias="xi-api-key"),
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    """Lists all saved cloned speaker profiles."""
    await verify_api_key(x_api_key=xi_api_key or x_api_key, authorization=authorization)
    profiles = [p.to_dict() for p in voice_cloning_engine.list_profiles()]
    return {"cloned_voices": profiles, "total": len(profiles)}


@router.delete("/api/v1/voices/cloned/{voice_id}")
async def delete_cloned_voice(
    voice_id: str,
    xi_api_key: Optional[str] = Header(default=None, alias="xi-api-key"),
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    """Deletes a saved cloned voice profile."""
    await verify_api_key(x_api_key=xi_api_key or x_api_key, authorization=authorization)
    success = voice_cloning_engine.delete_profile(voice_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "VOICE_NOT_FOUND", "message": f"Cloned voice '{voice_id}' not found."},
        )
    return {"status": "deleted", "voice_id": voice_id}
