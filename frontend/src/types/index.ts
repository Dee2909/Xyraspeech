export type SupportedLanguage = "ta" | "en" | "ta-en" | "auto";

export interface SpeechSegment {
  text: string;
  emotion: string;
  style: string;
  energy: number;
  speed: number;
  pitch: number;
  emphasis: string[];
  pause_before_ms: number;
  pause_after_ms: number;
}

export interface SpeechDirection {
  language: string;
  speech_text: string;
  overall_style: string;
  overall_emotion: string;
  segments: SpeechSegment[];
  metadata: {
    model: string;
    processing_mode: string;
    processing_time_ms: number;
  };
}

export interface VoiceItem {
  id: string;
  name: string;
  language: string;
  gender: string;
  engine: string;
  sample_rate: number;
  capabilities: string[];
  is_default: boolean;
  description?: string;
}

export interface ConversationResponse {
  conversation_id: string;
  user_input: string;
  response_text: string;
  language: string;
  intent: string;
  speech_direction: SpeechDirection;
  audio_base64?: string;
  latency_metrics: {
    brain_ms: number;
    tts_first_audio_ms: number;
    total_ms: number;
  };
}

export interface STTResponse {
  text: string;
  language: string;
  duration_seconds: number;
  confidence: number;
  model: string;
}

export interface TranslationResponse {
  source_text: string;
  translated_text: string;
  source_language: string;
  target_language: string;
  model: string;
}

export interface ModelHealthStatus {
  status: string;
  engines: {
    stt: { engine: string; model: string; available: boolean };
    tts: { engine: string; available: boolean; voice_count: number };
    brain_llm: { engine: string; model: string; reachable: boolean; model_available: boolean };
    translation: { engine: string; available: boolean };
  };
}
