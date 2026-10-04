import React, { useState, useRef } from "react";
import { Mic, Square, Upload, Copy, Check, RefreshCw } from "lucide-react";
import { api } from "../services/api";
import { STTResponse } from "../types";

export const SpeechToTextStudio: React.FC = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [language, setLanguage] = useState<string>("auto");
  const [result, setResult] = useState<STTResponse | null>(null);
  const [copied, setCopied] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        stream.getTracks().forEach((track) => track.stop());
        await handleTranscribe(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      alert("Microphone access failed.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    await handleTranscribe(file);
  };

  const handleTranscribe = async (audioBlob: Blob) => {
    setIsTranscribing(true);
    try {
      const sttRes = await api.transcribeAudio(audioBlob, language === "auto" ? undefined : language);
      setResult(sttRes);
    } catch (err: any) {
      alert(`STT Error: ${err.message}`);
    } finally {
      setIsTranscribing(false);
    }
  };

  const copyTranscript = () => {
    if (result?.text) {
      navigator.clipboard.writeText(result.text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
      {/* Audio Capture Card */}
      <div className="glass-card" style={{ padding: "24px", display: "flex", flexDirection: "column", gap: "20px" }}>
        <h2 style={{ fontSize: "18px", fontWeight: 700 }}>Speech-to-Text Input</h2>

        <div>
          <label style={{ fontSize: "13px", color: "var(--text-secondary)", display: "block", marginBottom: "6px" }}>Expected Language</label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            style={{ width: "100%", background: "rgba(255,255,255,0.06)", color: "white", border: "1px solid var(--border-color)", padding: "10px 14px", borderRadius: "8px", outline: "none" }}
          >
            <option value="auto">🌐 Auto-Detect Language</option>
            <option value="ta">🇮🇳 Tamil (தமிழ்)</option>
            <option value="en">🇬🇧 English</option>
          </select>
        </div>

        {/* Big Record Button */}
        <div style={{ padding: "30px", border: "2px dashed var(--border-color)", borderRadius: "16px", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: "16px" }}>
          <button
            onClick={isRecording ? stopRecording : startRecording}
            style={{
              width: "72px",
              height: "72px",
              borderRadius: "50%",
              border: "none",
              background: isRecording ? "var(--accent-rose)" : "linear-gradient(135deg, var(--accent-cyan), var(--accent-indigo))",
              color: "white",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
            }}
            className={isRecording ? "pulse-anim" : ""}
          >
            {isRecording ? <Square size={28} fill="white" /> : <Mic size={32} />}
          </button>
          <span style={{ fontSize: "14px", fontWeight: 600, color: isRecording ? "var(--accent-rose)" : "var(--text-secondary)" }}>
            {isRecording ? "Recording in progress... (Click to stop)" : "Click to start microphone recording"}
          </span>
        </div>

        {/* File Upload Option */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <label
            style={{
              flex: 1,
              padding: "12px 18px",
              background: "rgba(255,255,255,0.06)",
              border: "1px solid var(--border-color)",
              borderRadius: "10px",
              color: "white",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "8px",
              fontWeight: 600,
              fontSize: "14px",
            }}
          >
            <Upload size={16} /> Upload Audio File (.wav, .mp3)
            <input type="file" accept="audio/*" onChange={handleFileUpload} style={{ display: "none" }} />
          </label>
        </div>
      </div>

      {/* Transcription Output Card */}
      <div className="glass-card" style={{ padding: "24px", display: "flex", flexDirection: "column", gap: "16px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h2 style={{ fontSize: "18px", fontWeight: 700 }}>Transcription Result</h2>
          {result && (
            <button
              onClick={copyTranscript}
              style={{
                background: "rgba(255,255,255,0.08)",
                border: "none",
                color: "white",
                padding: "6px 12px",
                borderRadius: "6px",
                fontSize: "12px",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "4px",
              }}
            >
              {copied ? <Check size={14} color="var(--accent-emerald)" /> : <Copy size={14} />}
              {copied ? "Copied!" : "Copy Text"}
            </button>
          )}
        </div>

        <div
          style={{
            flex: 1,
            minHeight: "220px",
            background: "rgba(255,255,255,0.04)",
            border: "1px solid var(--border-color)",
            borderRadius: "12px",
            padding: "18px",
            color: "white",
            fontSize: "16px",
            lineHeight: "1.6",
            overflowY: "auto",
          }}
          className="tamil-text"
        >
          {isTranscribing ? (
            <div style={{ display: "flex", alignItems: "center", gap: "10px", color: "var(--accent-cyan)" }}>
              <RefreshCw className="pulse-anim" size={18} /> Transcribing speech using faster-whisper...
            </div>
          ) : result ? (
            <div>{result.text}</div>
          ) : (
            <div style={{ color: "var(--text-muted)", fontSize: "14px" }}>Record speech or upload an audio file to see transcript.</div>
          )}
        </div>

        {result && (
          <div style={{ display: "flex", gap: "16px", fontSize: "13px", color: "var(--text-secondary)", borderTop: "1px solid var(--border-color)", paddingTop: "12px" }}>
            <div>Language: <strong style={{ color: "var(--accent-cyan)" }}>{result.language.toUpperCase()}</strong></div>
            <div>Confidence: <strong style={{ color: "var(--accent-emerald)" }}>{Math.round(result.confidence * 100)}%</strong></div>
            <div>Duration: <strong>{result.duration_seconds}s</strong></div>
            <div>Model: <strong>{result.model}</strong></div>
          </div>
        )}
      </div>
    </div>
  );
};
