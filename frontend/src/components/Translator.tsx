import React, { useState } from "react";
import { ArrowLeftRight, Volume2, RefreshCw, Copy, Check } from "lucide-react";
import { api } from "../services/api";
import { TranslationResponse } from "../types";

export const Translator: React.FC = () => {
  const [sourceText, setSourceText] = useState("வணக்கம், நீங்கள் இன்று எவ்வாறு உணர்கிறீர்கள்?");
  const [sourceLang, setSourceLang] = useState<"ta" | "en">("ta");
  const [targetLang, setTargetLang] = useState<"ta" | "en">("en");
  const [isTranslating, setIsTranslating] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [result, setResult] = useState<TranslationResponse | null>(null);
  const [copied, setCopied] = useState(false);

  const handleSwap = () => {
    setSourceLang(targetLang);
    setTargetLang(sourceLang);
    if (result) {
      setSourceText(result.translated_text);
      setResult(null);
    }
  };

  const handleTranslate = async () => {
    if (!sourceText.trim()) return;
    setIsTranslating(true);
    try {
      const res = await api.translateText({
        text: sourceText,
        source_language: sourceLang,
        target_language: targetLang,
      });
      setResult(res);
    } catch (err: any) {
      alert(`Translation Error: ${err.message}`);
    } finally {
      setIsTranslating(false);
    }
  };

  const speakOutput = async () => {
    if (!result?.translated_text) return;
    setIsSpeaking(true);
    try {
      const blob = await api.synthesizeSpeech({
        text: result.translated_text,
        language: targetLang,
      });
      const audio = new Audio(URL.createObjectURL(blob));
      audio.onended = () => setIsSpeaking(false);
      audio.play();
    } catch (err: any) {
      alert(`Speech Error: ${err.message}`);
      setIsSpeaking(false);
    }
  };

  const copyText = () => {
    if (result?.translated_text) {
      navigator.clipboard.writeText(result.translated_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="glass-card" style={{ padding: "24px", display: "flex", flexDirection: "column", gap: "20px" }}>
      {/* Header Controls */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", borderBottom: "1px solid var(--border-color)", paddingBottom: "16px" }}>
        <h2 style={{ fontSize: "18px", fontWeight: 700 }}>Tamil ↔ English Neural Translator</h2>

        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <span style={{ fontWeight: 600, color: "var(--accent-cyan)" }}>
            {sourceLang === "ta" ? "Tamil (தமிழ்)" : "English"}
          </span>
          <button
            onClick={handleSwap}
            style={{
              padding: "8px 12px",
              background: "rgba(255,255,255,0.08)",
              border: "1px solid var(--border-color)",
              borderRadius: "8px",
              color: "white",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "4px",
            }}
          >
            <ArrowLeftRight size={14} /> Swap
          </button>
          <span style={{ fontWeight: 600, color: "var(--accent-indigo)" }}>
            {targetLang === "ta" ? "Tamil (தமிழ்)" : "English"}
          </span>
        </div>
      </div>

      {/* Input / Output Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
        {/* Source Box */}
        <div>
          <label style={{ fontSize: "12px", color: "var(--text-muted)", display: "block", marginBottom: "6px" }}>SOURCE TEXT</label>
          <textarea
            value={sourceText}
            onChange={(e) => setSourceText(e.target.value)}
            rows={8}
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
            }}
          />
        </div>

        {/* Target Box */}
        <div>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
            <label style={{ fontSize: "12px", color: "var(--text-muted)" }}>TRANSLATED TEXT</label>
            {result && (
              <button onClick={copyText} style={{ background: "none", border: "none", color: "var(--accent-cyan)", cursor: "pointer", fontSize: "12px", display: "flex", alignItems: "center", gap: "4px" }}>
                {copied ? <Check size={12} /> : <Copy size={12} />} {copied ? "Copied" : "Copy"}
              </button>
            )}
          </div>
          <div
            style={{
              height: "216px",
              background: "rgba(255,255,255,0.02)",
              border: "1px solid var(--border-color)",
              borderRadius: "12px",
              padding: "16px",
              color: "white",
              fontSize: "16px",
              lineHeight: "1.6",
              overflowY: "auto",
            }}
            className="tamil-text"
          >
            {isTranslating ? (
              <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "var(--accent-cyan)" }}>
                <RefreshCw className="pulse-anim" size={16} /> Translating with neural engine...
              </div>
            ) : result ? (
              result.translated_text
            ) : (
              <div style={{ color: "var(--text-muted)", fontSize: "14px" }}>Click Translate to generate output.</div>
            )}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div style={{ display: "flex", gap: "12px" }}>
        <button
          onClick={handleTranslate}
          disabled={isTranslating}
          style={{
            flex: 1,
            padding: "14px",
            background: "linear-gradient(135deg, var(--accent-cyan), var(--accent-indigo))",
            border: "none",
            borderRadius: "12px",
            color: "white",
            fontWeight: 700,
            fontSize: "15px",
            cursor: "pointer",
          }}
        >
          {isTranslating ? "Translating..." : "Translate Text"}
        </button>

        {result && (
          <button
            onClick={speakOutput}
            disabled={isSpeaking}
            style={{
              padding: "14px 24px",
              background: "rgba(16,185,129,0.2)",
              border: "1px solid var(--accent-emerald)",
              borderRadius: "12px",
              color: "var(--accent-emerald)",
              fontWeight: 600,
              fontSize: "14px",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <Volume2 size={16} /> {isSpeaking ? "Speaking..." : "Speak Output"}
          </button>
        )}
      </div>
    </div>
  );
};
