import React, { useState, useRef } from "react";
import { Copy, Mic, Upload, Play, Square, Sparkles, CheckCircle2, AlertCircle } from "lucide-react";

export const VoiceCloningStudio: React.FC = () => {
  const [voiceName, setVoiceName] = useState("My Cloned Voice");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordedAudioBlob, setRecordedAudioBlob] = useState<Blob | null>(null);
  const [recordedAudioUrl, setRecordedAudioUrl] = useState<string | null>(null);
  const [clonedProfile, setClonedProfile] = useState<any | null>(null);

  const [targetText, setTargetText] = useState("வணக்கம்! இது என் சொந்த குரலில் பேசும் குளோனிங் தொழில்நுட்பம்.");
  const [targetLang, setTargetLang] = useState<"ta" | "en">("ta");
  const [isSynthesizing, setIsSynthesizing] = useState(false);
  const [generatedAudioUrl, setGeneratedAudioUrl] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // Start Mic Recording
  const startRecording = async () => {
    try {
      setErrorMsg(null);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        setRecordedAudioBlob(audioBlob);
        setRecordedAudioUrl(URL.createObjectURL(audioBlob));
        setSelectedFile(null);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err: any) {
      setErrorMsg("Microphone permission denied: " + err.message);
    }
  };

  // Stop Mic Recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach((t) => t.stop());
      setIsRecording(false);
    }
  };

  // Handle File Selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setRecordedAudioBlob(null);
      setRecordedAudioUrl(URL.createObjectURL(file));
      setErrorMsg(null);
    }
  };

  // Clone & Synthesize
  const handleCloneAndSpeak = async () => {
    const audioToUse = selectedFile || recordedAudioBlob;
    if (!audioToUse) {
      setErrorMsg("Please upload an audio file or record 3 seconds of your voice first.");
      return;
    }
    if (!targetText.trim()) {
      setErrorMsg("Please enter text to speak.");
      return;
    }

    setIsSynthesizing(true);
    setErrorMsg(null);

    try {
      const formData = new FormData();
      formData.append("text", targetText);
      formData.append("reference_audio", audioToUse, "reference.wav");
      formData.append("voice_name", voiceName);
      formData.append("language", targetLang);
      formData.append("emotion", "warm");

      const response = await fetch("http://127.0.0.1:8000/api/v1/tts/clone", {
        method: "POST",
        headers: {
          "X-API-Key": "xyra_live_8f3a9b2c1d4e7f6a5b0c9d8e7f6a5b4c",
        },
        body: formData,
      });

      if (!response.ok) {
        const errJson = await response.json();
        throw new Error(errJson.error?.message || "Voice cloning failed.");
      }

      const blob = await response.blob();
      const audioUrl = URL.createObjectURL(blob);
      setGeneratedAudioUrl(audioUrl);

      // Extract metadata from headers
      const voiceId = response.headers.get("X-Voice-Id");
      const gender = response.headers.get("X-Gender");
      setClonedProfile({ voice_id: voiceId, gender: gender, name: voiceName });

      // Automatically play
      const audio = new Audio(audioUrl);
      audio.play();
    } catch (err: any) {
      setErrorMsg(err.message || "An error occurred during voice cloning.");
    } finally {
      setIsSynthesizing(false);
    }
  };

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1.2fr", gap: "24px" }}>
      {/* Step 1: Reference Audio Input */}
      <div className="glass-panel" style={{ padding: "24px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "16px" }}>
          <Copy size={20} color="var(--accent-cyan)" />
          <h2 style={{ fontSize: "18px", fontWeight: 700 }}>1. Provide Reference Voice</h2>
        </div>

        <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginBottom: "20px" }}>
          Upload a clear 3-10 second audio clip of your voice or record directly from your microphone.
        </p>

        {/* Voice Name Input */}
        <div style={{ marginBottom: "16px" }}>
          <label style={{ fontSize: "12px", color: "var(--text-muted)", fontWeight: 600, display: "block", marginBottom: "6px" }}>
            VOICE PROFILE NAME
          </label>
          <input
            type="text"
            value={voiceName}
            onChange={(e) => setVoiceName(e.target.value)}
            style={{
              width: "100%",
              padding: "10px 12px",
              borderRadius: "8px",
              border: "1px solid var(--border-color)",
              background: "rgba(255,255,255,0.03)",
              color: "white",
              fontSize: "14px",
            }}
          />
        </div>

        {/* Record or Upload Controls */}
        <div style={{ display: "flex", gap: "12px", marginBottom: "20px" }}>
          {/* Record Button */}
          {!isRecording ? (
            <button
              onClick={startRecording}
              style={{
                flex: 1,
                padding: "12px",
                borderRadius: "10px",
                border: "1px solid rgba(239,68,68,0.4)",
                background: "rgba(239,68,68,0.1)",
                color: "#ef4444",
                fontWeight: 600,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
                cursor: "pointer",
              }}
            >
              <Mic size={18} /> Record Voice
            </button>
          ) : (
            <button
              onClick={stopRecording}
              style={{
                flex: 1,
                padding: "12px",
                borderRadius: "10px",
                border: "none",
                background: "#ef4444",
                color: "white",
                fontWeight: 600,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
                cursor: "pointer",
                animation: "pulse 1.5s infinite",
              }}
            >
              <Square size={18} /> Stop Recording
            </button>
          )}

          {/* File Upload Label */}
          <label
            style={{
              flex: 1,
              padding: "12px",
              borderRadius: "10px",
              border: "1px solid var(--border-color)",
              background: "rgba(255,255,255,0.05)",
              color: "var(--text-secondary)",
              fontWeight: 600,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "8px",
              cursor: "pointer",
              textAlign: "center",
            }}
          >
            <Upload size={18} /> Upload Audio
            <input type="file" accept="audio/*" onChange={handleFileChange} style={{ display: "none" }} />
          </label>
        </div>

        {/* Audio Preview */}
        {recordedAudioUrl && (
          <div style={{ padding: "14px", borderRadius: "10px", background: "rgba(255,255,255,0.02)", border: "1px solid var(--border-color)", marginBottom: "16px" }}>
            <div style={{ fontSize: "12px", color: "var(--accent-cyan)", fontWeight: 600, marginBottom: "8px", display: "flex", alignItems: "center", gap: "6px" }}>
              <CheckCircle2 size={14} /> Reference Voice Loaded
            </div>
            <audio controls src={recordedAudioUrl} style={{ width: "100%", height: "36px" }} />
          </div>
        )}
      </div>

      {/* Step 2: Target Text & Generation */}
      <div className="glass-panel" style={{ padding: "24px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "16px" }}>
          <Sparkles size={20} color="var(--accent-indigo)" />
          <h2 style={{ fontSize: "18px", fontWeight: 700 }}>2. Replicate Voice on Target Text</h2>
        </div>

        {/* Language Selection */}
        <div style={{ display: "flex", gap: "8px", marginBottom: "14px" }}>
          <button
            onClick={() => setTargetLang("ta")}
            style={{
              padding: "6px 14px",
              borderRadius: "6px",
              border: "none",
              background: targetLang === "ta" ? "var(--accent-cyan)" : "rgba(255,255,255,0.05)",
              color: targetLang === "ta" ? "black" : "white",
              fontWeight: 600,
              fontSize: "12px",
              cursor: "pointer",
            }}
          >
            Tamil (தமிழ்)
          </button>
          <button
            onClick={() => setTargetLang("en")}
            style={{
              padding: "6px 14px",
              borderRadius: "6px",
              border: "none",
              background: targetLang === "en" ? "var(--accent-cyan)" : "rgba(255,255,255,0.05)",
              color: targetLang === "en" ? "black" : "white",
              fontWeight: 600,
              fontSize: "12px",
              cursor: "pointer",
            }}
          >
            English
          </button>
        </div>

        {/* Text Area */}
        <textarea
          value={targetText}
          onChange={(e) => setTargetText(e.target.value)}
          placeholder="Enter Tamil or English text to speak in the cloned voice..."
          rows={5}
          style={{
            width: "100%",
            padding: "14px",
            borderRadius: "10px",
            border: "1px solid var(--border-color)",
            background: "rgba(255,255,255,0.03)",
            color: "white",
            fontSize: "15px",
            lineHeight: 1.6,
            resize: "none",
            marginBottom: "16px",
            fontFamily: "inherit",
          }}
        />

        {errorMsg && (
          <div style={{ padding: "10px 14px", borderRadius: "8px", background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)", color: "#ef4444", fontSize: "13px", marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
            <AlertCircle size={16} /> {errorMsg}
          </div>
        )}

        {/* Action Button */}
        <button
          onClick={handleCloneAndSpeak}
          disabled={isSynthesizing}
          style={{
            width: "100%",
            padding: "14px",
            borderRadius: "10px",
            border: "none",
            background: "linear-gradient(135deg, var(--accent-cyan), var(--accent-indigo))",
            color: "white",
            fontWeight: 700,
            fontSize: "15px",
            cursor: isSynthesizing ? "not-allowed" : "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "8px",
            boxShadow: "0 4px 20px rgba(6,182,212,0.3)",
          }}
        >
          {isSynthesizing ? (
            <>Processing Neural Voice Cloning...</>
          ) : (
            <>
              <Play size={18} fill="white" /> Clone & Generate Speech
            </>
          )}
        </button>

        {/* Cloned Audio Result Player */}
        {generatedAudioUrl && (
          <div style={{ marginTop: "24px", padding: "18px", borderRadius: "12px", background: "rgba(6,182,212,0.05)", border: "1px solid rgba(6,182,212,0.3)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
              <span style={{ fontSize: "13px", fontWeight: 700, color: "var(--accent-cyan)" }}>
                ✨ Cloned Voice Output ({clonedProfile?.gender || "Neural"})
              </span>
              <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>24,000 Hz Studio WAV</span>
            </div>
            <audio controls src={generatedAudioUrl} autoPlay style={{ width: "100%", height: "40px" }} />
          </div>
        )}
      </div>
    </div>
  );
};
