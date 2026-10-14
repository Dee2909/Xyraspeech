import {
  ConversationResponse,
  ModelHealthStatus,
  STTResponse,
  TranslationResponse,
  VoiceItem,
} from "../types";

const BASE_URL = "";

async function safeJsonParse(res: Response): Promise<any> {
  try {
    const text = await res.text();
    return text ? JSON.parse(text) : {};
  } catch {
    return {};
  }
}

export const api = {
  async getHealth(): Promise<{ status: string }> {
    try {
      const res = await fetch(`${BASE_URL}/health`);
      if (!res.ok) return { status: "offline" };
      return await safeJsonParse(res);
    } catch {
      return { status: "offline" };
    }
  },

  async getModelsHealth(): Promise<ModelHealthStatus> {
    try {
      const res = await fetch(`${BASE_URL}/health/models`);
      if (!res.ok) return {} as ModelHealthStatus;
      return await safeJsonParse(res);
    } catch {
      return {} as ModelHealthStatus;
    }
  },

  async getVoices(): Promise<VoiceItem[]> {
    try {
      const res = await fetch(`${BASE_URL}/api/v1/voices`);
      if (!res.ok) {
        console.warn("Voices endpoint returned status:", res.status);
        return [];
      }
      const data = await safeJsonParse(res);
      return data.voices || [];
    } catch (err) {
      console.error("Failed fetching voices:", err);
      return [];
    }
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
      const err = await safeJsonParse(res);
      throw new Error(err.detail?.message || err.error?.message || `Synthesis failed (HTTP ${res.status})`);
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
      const err = await safeJsonParse(res);
      throw new Error(err.detail?.message || err.error?.message || `Transcription failed (HTTP ${res.status})`);
    }
    return safeJsonParse(res);
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
      const err = await safeJsonParse(res);
      throw new Error(err.detail?.message || err.error?.message || `Translation failed (HTTP ${res.status})`);
    }
    return safeJsonParse(res);
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
      const err = await safeJsonParse(res);
      throw new Error(err.detail?.message || err.error?.message || `Conversation failed (HTTP ${res.status})`);
    }
    return safeJsonParse(res);
  },

  async cloneVoice(audioFile: File, voiceName: string, language: string = "ta", description?: string): Promise<{ status: string; voice: VoiceItem; message: string }> {
    const formData = new FormData();
    formData.append("file", audioFile);
    formData.append("voice_name", voiceName);
    formData.append("language", language);
    if (description) formData.append("description", description);

    const res = await fetch(`${BASE_URL}/api/v1/voices/clone`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await safeJsonParse(res);
      throw new Error(err.detail?.message || err.message || `Voice cloning failed (HTTP ${res.status})`);
    }
    return safeJsonParse(res);
  },

  async cloneVoice(params: {
    file: Blob;
    name: string;
    language?: string;
    gender?: string;
    description?: string;
  }): Promise<VoiceItem> {
    const formData = new FormData();
    formData.append("file", params.file, "voice_sample.wav");
    formData.append("name", params.name);
    if (params.language) formData.append("language", params.language);
    if (params.gender) formData.append("gender", params.gender);
    if (params.description) formData.append("description", params.description);

    const res = await fetch(`${BASE_URL}/api/v1/voices/clone`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error?.message || "Voice cloning failed");
    }
    return res.json();
  },

  async deleteVoice(voiceId: string): Promise<void> {
    const res = await fetch(`${BASE_URL}/api/v1/voices/${voiceId}`, {
      method: "DELETE",
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error?.message || "Deleting voice failed");
    }
  },
};
