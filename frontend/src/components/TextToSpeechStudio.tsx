import React, { useState } from "react";
import { Play, Download, RefreshCw, Volume2, Sliders } from "lucide-react";
import { api } from "../services/api";
import { VoiceItem } from "../types";

interface Props {
  voices: VoiceItem[];
}

export const TextToSpeechStudio: React.FC<Props> = ({ voices }) => {
  const [text, setText] = useState<string>("வணக்கம்! XyraSpeech தயாரிப்பு மேடைக்கு தங்களை அன்புடன் வரவேற்கிறோம்!");
  const [language, setLanguage] = useState<string>("ta");
  const [selectedVoice, setSelectedVoice] = useState<string>("ta_vani");
  const [speed, setSpeed] = useState<number>(1.0);
  const [pitch, setPitch] = useState<number>(1.0);
  const [energy, setEnergy] = useState<number>(0.6);
  const [isSynthesizing, setIsSynthesizing] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  const handleSynthesize = async () => {
    if (!text.trim()) return;
    setIsSynthesizing(true);
    try {
      const blob = await api.synthesizeSpeech({
        text,
        language,
        voice_id: selectedVoice,
        speed,
        pitch,
        energy,
      });
      const url = URL.createObjectURL(blob);
      setAudioUrl(url);

      const audio = new Audio(url);
      audio.play();
    } catch (err: any) {
      alert(`Synthesis Error: ${err.message}`);
    } finally {
      setIsSynthesizing(false);
    }
  };

  const setSample = (type: "tamil" | "english" | "mixed") => {
    if (type === "tamil") {
      setText("வணக்கம்! இன்று வானிலை மிகவும் இனிமையாக உள்ளது.");
      setLanguage("ta");
      setSelectedVoice("ta_vani");
    } else if (type === "english") {
      setText("Hello! Welcome to XyraSpeech studio, a local-first speech synthesis platform.");
      setLanguage("en");
      setSelectedVoice("en_rishi");
    } else {
      setText("Hello friends! இன்று meeting ரொம்ப important, please attend பண்ணுங்க.");
      setLanguage("ta-en");
      setSelectedVoice("ta_vani");
    }
  };

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 360px", gap: "24px" }}>
      {/* Text Area & Generation */}
      <div className="glass-card" style={{ padding: "24px", display: "flex", flexDirection: "column", gap: "16px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h2 style={{ fontSize: "18px", fontWeight: 700 }}>Text-to-Speech Studio</h2>
          <div style={{ display: "flex", gap: "8px" }}>
            <button onClick={() => setSample("tamil")} style={{ background: "rgba(255,255,255,0.08)", border: "none", color: "white", padding: "6px 12px", borderRadius: "6px", fontSize: "12px", cursor: "pointer" }}>Tamil Sample</button>
            <button onClick={() => setSample("english")} style={{ background: "rgba(255,255,255,0.08)", border: "none", color: "white", padding: "6px 12px", borderRadius: "6px", fontSize: "12px", cursor: "pointer" }}>English Sample</button>
            <button onClick={() => setSample("mixed")} style={{ background: "rgba(255,255,255,0.08)", border: "none", color: "white", padding: "6px 12px", borderRadius: "6px", fontSize: "12px", cursor: "pointer" }}>Mixed Sample</button>
          </div>
        </div>

        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={7}
          placeholder="Enter Tamil or English text to synthesize..."
          className="tamil-text"
          style={{
            width: "100%",
            background: "rgba(255,255,255,0.04)",
            border: "1px solid var(--border-color)",
            borderRadius: "12px",
            color: "white",
            padding: "16px",
            fontSize: "16px",
            lineHeight: "1.6",
            outline: "none",
            resize: "vertical",
          }}
        />

        <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
          <button
            onClick={handleSynthesize}
            disabled={isSynthesizing}
            style={{
              flex: 1,
              padding: "14px 24px",
              background: isSynthesizing ? "rgba(255,255,255,0.2)" : "linear-gradient(135deg, var(--accent-cyan), var(--accent-indigo))",
              border: "none",
              borderRadius: "12px",
              color: "white",
              fontWeight: 700,
              fontSize: "15px",
              cursor: isSynthesizing ? "not-allowed" : "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "8px",
            }}
          >
            {isSynthesizing ? <RefreshCw className="pulse-anim" size={18} /> : <Play size={18} />}
            {isSynthesizing ? "Synthesizing Speech..." : "Generate & Play Audio"}
          </button>

          {audioUrl && (
            <a
              href={audioUrl}
              download="xyraspeech-generated.wav"
              style={{
                padding: "14px 18px",
                background: "rgba(255,255,255,0.08)",
                border: "1px solid var(--border-color)",
                borderRadius: "12px",
                color: "white",
                textDecoration: "none",
                display: "flex",
                alignItems: "center",
                gap: "6px",
                fontWeight: 600,
                fontSize: "14px",
              }}
            >
              <Download size={16} /> Download WAV
            </a>
          )}
        </div>

        {audioUrl && (
          <div style={{ marginTop: "12px", padding: "16px", background: "rgba(255,255,255,0.04)", borderRadius: "12px", display: "flex", alignItems: "center", gap: "12px" }}>
            <Volume2 size={20} color="var(--accent-emerald)" />
            <audio controls src={audioUrl} style={{ width: "100%", outline: "none" }} />
          </div>
        )}
      </div>

      {/* Voice & Prosody Controls */}
      <div className="glass-card" style={{ padding: "24px", display: "flex", flexDirection: "column", gap: "20px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <Sliders size={18} color="var(--accent-cyan)" />
          <h3 style={{ fontSize: "16px", fontWeight: 700 }}>Voice & Prosody</h3>
        </div>

        <div>
          <label style={{ fontSize: "13px", color: "var(--text-secondary)", display: "block", marginBottom: "6px" }}>Voice Actor</label>
          <select
            value={selectedVoice}
            onChange={(e) => setSelectedVoice(e.target.value)}
            style={{ width: "100%", background: "rgba(255,255,255,0.06)", color: "white", border: "1px solid var(--border-color)", padding: "10px 14px", borderRadius: "8px", outline: "none" }}
          >
            {voices.map((v) => (
              <option key={v.id} value={v.id}>
                {v.name} ({v.gender})
              </option>
            ))}
          </select>
        </div>

        <div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", marginBottom: "6px" }}>
            <span style={{ color: "var(--text-secondary)" }}>Speech Rate (Speed)</span>
            <span style={{ fontWeight: 600, color: "var(--accent-cyan)" }}>{speed}x</span>
          </div>
          <input
            type="range"
            min={0.6}
            max={1.4}
            step={0.05}
            value={speed}
            onChange={(e) => setSpeed(parseFloat(e.target.value))}
            style={{ width: "100%" }}
          />
        </div>

        <div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", marginBottom: "6px" }}>
            <span style={{ color: "var(--text-secondary)" }}>Pitch Modifier</span>
            <span style={{ fontWeight: 600, color: "var(--accent-indigo)" }}>{pitch}x</span>
          </div>
          <input
            type="range"
            min={0.85}
            max={1.15}
            step={0.02}
            value={pitch}
            onChange={(e) => setPitch(parseFloat(e.target.value))}
            style={{ width: "100%" }}
          />
        </div>

        <div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", marginBottom: "6px" }}>
            <span style={{ color: "var(--text-secondary)" }}>Energy Level</span>
            <span style={{ fontWeight: 600, color: "var(--accent-emerald)" }}>{Math.round(energy * 100)}%</span>
          </div>
          <input
            type="range"
            min={0.1}
            max={1.0}
            step={0.05}
            value={energy}
            onChange={(e) => setEnergy(parseFloat(e.target.value))}
            style={{ width: "100%" }}
          />
        </div>
      </div>
    </div>
  );
};
