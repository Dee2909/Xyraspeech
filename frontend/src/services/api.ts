import {
  ConversationResponse,
  ModelHealthStatus,
  STTResponse,
  TranslationResponse,
  VoiceItem,
} from "../types";

const BASE_URL = "";

export const api = {
  async getHealth(): Promise<{ status: string }> {
    const res = await fetch(`${BASE_URL}/health`);
    return res.json();
  },

  async getModelsHealth(): Promise<ModelHealthStatus> {
    const res = await fetch(`${BASE_URL}/health/models`);
    return res.json();
  },

  async getVoices(): Promise<VoiceItem[]> {
    const res = await fetch(`${BASE_URL}/api/v1/voices`);
    const data = await res.json();
    return data.voices || [];
  },

  async synthesizeSpeech(params: {
    text: string;
    language?: string;
    voice_id?: string;
    speed?: number;
    pitch?: number;
    energy?: number;
    emotion?: string;
  }): Promise<Blob> {
    const res = await fetch(`${BASE_URL}/api/v1/tts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error?.message || "Synthesis failed");
    }
    return res.blob();
  },

  async transcribeAudio(file: Blob, language?: string): Promise<STTResponse> {
    const formData = new FormData();
    formData.append("file", file, "recording.wav");
    if (language && language !== "auto") {
      formData.append("language", language);
    }
    const res = await fetch(`${BASE_URL}/api/v1/stt`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error?.message || "Transcription failed");
    }
    return res.json();
  },

  async translateText(params: {
    text: string;
    source_language: string;
    target_language: string;
  }): Promise<TranslationResponse> {
    const res = await fetch(`${BASE_URL}/api/v1/translate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error?.message || "Translation failed");
    }
    return res.json();
  },

  async sendConversationMessage(params: {
    text: string;
    conversation_id?: string;
    language?: string;
    voice_id?: string;
  }): Promise<ConversationResponse> {
    const res = await fetch(`${BASE_URL}/api/v1/conversation/message`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error?.message || "Conversation processing failed");
    }
    return res.json();
  },
};
