import React, { useState } from "react";
import { Volume2, Mic, Trash2, Sparkles } from "lucide-react";
import { api } from "../services/api";
import { VoiceItem } from "../types";

interface Props {
  voices: VoiceItem[];
  onVoicesUpdated?: () => void;
}

export const VoiceLibrary: React.FC<Props> = ({ voices, onVoicesUpdated }) => {
  const [showCloneModal, setShowCloneModal] = useState(false);
  const [cloneName, setCloneName] = useState("");
  const [cloneLang, setCloneLang] = useState("ta");
  const [cloneGender, setCloneGender] = useState("Auto");
  const [cloneDesc, setCloneDesc] = useState("");
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [isCloning, setIsCloning] = useState(false);
  const [localVoices, setLocalVoices] = useState<VoiceItem[]>(voices);

  React.useEffect(() => {
    setLocalVoices(voices);
  }, [voices]);

  const previewVoice = async (voice: VoiceItem) => {
    try {
      const sampleText =
        voice.language === "ta"
          ? "வணக்கம்! எனது பெயர் எக்ஸ்ரா குரல். நான் உங்களின் புதிய குரல் உதவியாளர்."
          : `Hello! My name is ${voice.name.replace(/[^a-zA-Z ]/g, "").trim()}. I am your cloned voice actor.`;

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

  const handleCloneSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!cloneName.trim()) {
      alert("Please enter a speaker name.");
      return;
    }
    if (!audioFile) {
      alert("Please upload an audio sample file (WAV/MP3).");
      return;
    }

    try {
      setIsCloning(true);
      const newVoice = await api.cloneVoice({
        file: audioFile,
        name: cloneName.trim(),
        language: cloneLang,
        gender: cloneGender,
        description: cloneDesc.trim() || undefined,
      });
      alert(`Voice '${cloneName}' cloned successfully!`);
      setLocalVoices((prev) => [...prev.filter((v) => v.id !== newVoice.id), newVoice]);
      setShowCloneModal(false);
      setCloneName("");
      setCloneDesc("");
      setAudioFile(null);
      if (onVoicesUpdated) onVoicesUpdated();
    } catch (err: any) {
      alert(`Voice Cloning failed: ${err.message}`);
    } finally {
      setIsCloning(false);
    }
  };

  const handleDeleteVoice = async (voiceId: string, voiceName: string) => {
    if (!confirm(`Are you sure you want to delete cloned voice '${voiceName}'?`)) return;
    try {
      await api.deleteVoice(voiceId);
      setLocalVoices((prev) => prev.filter((v) => v.id !== voiceId));
      if (onVoicesUpdated) onVoicesUpdated();
    } catch (err: any) {
      alert(`Failed to delete voice: ${err.message}`);
    }
  };

  return (
    <div className="glass-card" style={{ padding: "28px" }}>
      {/* Hero Visual Banner */}
      <div
        style={{
          position: "relative",
          marginBottom: "28px",
          borderRadius: "18px",
          overflow: "hidden",
          border: "1px solid rgba(255, 255, 255, 0.12)",
          display: "flex",
          alignItems: "center",
          minHeight: "180px",
          background: "linear-gradient(90deg, rgba(13, 18, 34, 0.95) 45%, rgba(13, 18, 34, 0.35) 100%), url('/voice_clone_art.png') right center / cover no-repeat",
          padding: "32px",
        }}
      >
        <div style={{ maxWidth: "600px", zIndex: 2 }}>
          <span style={{ fontSize: "11px", textTransform: "uppercase", letterSpacing: "1px", color: "var(--accent-cyan)", fontWeight: 800 }}>
            ⚡ Zero-Shot Acoustic Feature Extraction
          </span>
          <h2 style={{ fontSize: "28px", fontWeight: 900, marginTop: "6px", fontFamily: "var(--font-heading)" }}>
            Neural <span className="gradient-text">Voice Cloning</span> Studio
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "14px", marginTop: "8px", lineHeight: "1.5" }}>
            Upload a short 5-second audio sample to extract pitch frequency (\(F_0\)), timbre dynamics, and formant response for instant speech synthesis.
          </p>
        </div>
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <div>
          <h3 style={{ fontSize: "18px", fontWeight: 700 }}>Voice Actor Library</h3>
          <p style={{ color: "var(--text-secondary)", fontSize: "14px", marginTop: "4px" }}>
            Installed genuine local neural voices and custom cloned speakers.
          </p>
        </div>
        <button
          className="shimmer-btn"
          onClick={() => setShowCloneModal(!showCloneModal)}
          style={{
            padding: "12px 20px",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            fontSize: "14px",
          }}
        >
          <Sparkles size={16} /> Clone New Voice
        </button>
      </div>

      {showCloneModal && (
        <div
          style={{
            marginBottom: "24px",
            padding: "20px",
            background: "rgba(99, 102, 241, 0.08)",
            border: "1px solid rgba(99, 102, 241, 0.3)",
            borderRadius: "14px",
          }}
        >
          <h3 style={{ fontSize: "16px", fontWeight: 700, marginBottom: "12px", display: "flex", alignItems: "center", gap: "8px" }}>
            <Mic size={18} color="var(--accent-purple)" /> Voice Cloning Studio
          </h3>
          <form onSubmit={handleCloneSubmit} style={{ display: "grid", gap: "14px" }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "12px" }}>
              <div>
                <label style={{ fontSize: "12px", color: "var(--text-secondary)", fontWeight: 600 }}>Speaker Name</label>
                <input
                  type="text"
                  placeholder="e.g. Karthik / Priya / My Voice"
                  value={cloneName}
                  onChange={(e) => setCloneName(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "10px",
                    background: "rgba(0,0,0,0.3)",
                    border: "1px solid var(--border-color)",
                    borderRadius: "8px",
                    color: "white",
                    marginTop: "4px",
                  }}
                  required
                />
              </div>
              <div>
                <label style={{ fontSize: "12px", color: "var(--text-secondary)", fontWeight: 600 }}>Language</label>
                <select
                  value={cloneLang}
                  onChange={(e) => setCloneLang(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "10px",
                    background: "rgba(0,0,0,0.3)",
                    border: "1px solid var(--border-color)",
                    borderRadius: "8px",
                    color: "white",
                    marginTop: "4px",
                  }}
                >
                  <option value="ta">Tamil (ta)</option>
                  <option value="en">English (en)</option>
                </select>
              </div>
              <div>
                <label style={{ fontSize: "12px", color: "var(--text-secondary)", fontWeight: 600 }}>Voice Gender</label>
                <select
                  value={cloneGender}
                  onChange={(e) => setCloneGender(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "10px",
                    background: "rgba(0,0,0,0.3)",
                    border: "1px solid var(--border-color)",
                    borderRadius: "8px",
                    color: "white",
                    marginTop: "4px",
                  }}
                >
                  <option value="Auto">✨ Auto Detect Pitch</option>
                  <option value="Female">👩 Female Voice</option>
                  <option value="Male">👨 Male Voice</option>
                </select>
              </div>
            </div>

            <div>
              <label style={{ fontSize: "12px", color: "var(--text-secondary)", fontWeight: 600 }}>Reference Audio Sample File (WAV/MP3)</label>
              <input
                type="file"
                accept="audio/*"
                onChange={(e) => setAudioFile(e.target.files?.[0] || null)}
                style={{
                  width: "100%",
                  padding: "8px",
                  background: "rgba(0,0,0,0.3)",
                  border: "1px solid var(--border-color)",
                  borderRadius: "8px",
                  color: "white",
                  marginTop: "4px",
                }}
                required
              />
            </div>

            <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end" }}>
              <button
                type="button"
                onClick={() => setShowCloneModal(false)}
                style={{
                  padding: "8px 16px",
                  background: "rgba(255,255,255,0.1)",
                  border: "none",
                  borderRadius: "8px",
                  color: "white",
                  cursor: "pointer",
                }}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isCloning}
                style={{
                  padding: "8px 20px",
                  background: "var(--accent-purple)",
                  border: "none",
                  borderRadius: "8px",
                  color: "white",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                {isCloning ? "Cloning Voice..." : "Clone Voice"}
              </button>
            </div>
          </form>
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "16px" }}>
        {localVoices.map((v) => (
          <div
            key={v.id}
            style={{
              padding: "20px",
              background: v.engine === "voice_cloner" ? "rgba(99, 102, 241, 0.08)" : "rgba(255,255,255,0.04)",
              border: v.engine === "voice_cloner" ? "1px solid rgba(99, 102, 241, 0.4)" : "1px solid var(--border-color)",
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
              {v.is_default ? (
                <span style={{ fontSize: "11px", background: "rgba(16,185,129,0.2)", color: "var(--accent-emerald)", padding: "3px 8px", borderRadius: "10px", fontWeight: 600 }}>
                  Default
                </span>
              ) : v.engine === "voice_cloner" ? (
                <button
                  onClick={() => handleDeleteVoice(v.id, v.name)}
                  style={{ background: "none", border: "none", color: "#ef4444", cursor: "pointer" }}
                  title="Delete Cloned Voice"
                >
                  <Trash2 size={16} />
                </button>
              ) : null}
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
