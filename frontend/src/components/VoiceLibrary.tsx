import React from "react";
import { Volume2 } from "lucide-react";
import { api } from "../services/api";
import { VoiceItem } from "../types";

interface Props {
  voices: VoiceItem[];
}

export const VoiceLibrary: React.FC<Props> = ({ voices }) => {
  const previewVoice = async (voice: VoiceItem) => {
    try {
      const sampleText =
        voice.language === "ta"
          ? "வணக்கம்! எனது பெயர் வாணி. நான் உங்கள் தமிழ் குரல் உதவியாளர்."
          : `Hello! My name is ${voice.name.split(" ")[0]}. I am your voice actor.`;

      const blob = await api.synthesizeSpeech({
        text: sampleText,
        language: voice.language,
        voice_id: voice.id,
      });

      const audio = new Audio(URL.createObjectURL(blob));
      audio.play();
    } catch (err: any) {
      alert(`Preview failed: ${err.message}`);
    }
  };

  return (
    <div className="glass-card" style={{ padding: "24px" }}>
      <div style={{ marginBottom: "20px" }}>
        <h2 style={{ fontSize: "18px", fontWeight: 700 }}>Voice Actor Library</h2>
        <p style={{ color: "var(--text-secondary)", fontSize: "14px", marginTop: "4px" }}>
          Explore genuine installed local voice profiles for Tamil and English synthesis.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "16px" }}>
        {voices.map((v) => (
          <div
            key={v.id}
            style={{
              padding: "20px",
              background: "rgba(255,255,255,0.04)",
              border: "1px solid var(--border-color)",
              borderRadius: "14px",
              display: "flex",
              flexDirection: "column",
              gap: "12px",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div>
                <h4 style={{ fontSize: "16px", fontWeight: 700 }}>{v.name}</h4>
                <span style={{ fontSize: "12px", color: "var(--accent-cyan)", textTransform: "uppercase", fontWeight: 600 }}>
                  {v.language === "ta" ? "🇮🇳 Tamil" : "🇬🇧 English"} • {v.gender}
                </span>
              </div>
              {v.is_default && (
                <span style={{ fontSize: "11px", background: "rgba(16,185,129,0.2)", color: "var(--accent-emerald)", padding: "3px 8px", borderRadius: "10px", fontWeight: 600 }}>
                  Default
                </span>
              )}
            </div>

            <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: "1.5" }}>
              {v.description || "High-fidelity local speech synthesis voice profile."}
            </p>

            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
              {v.capabilities.map((c) => (
                <span key={c} style={{ fontSize: "11px", background: "rgba(255,255,255,0.06)", padding: "2px 6px", borderRadius: "4px", color: "var(--text-muted)" }}>
                  ✓ {c}
                </span>
              ))}
            </div>

            <button
              onClick={() => previewVoice(v)}
              style={{
                marginTop: "4px",
                padding: "10px",
                background: "rgba(255,255,255,0.08)",
                border: "1px solid var(--border-color)",
                borderRadius: "8px",
                color: "white",
                cursor: "pointer",
                fontWeight: 600,
                fontSize: "13px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "6px",
              }}
            >
              <Volume2 size={14} /> Preview Voice Audio
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
