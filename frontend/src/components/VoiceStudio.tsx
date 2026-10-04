import React, { useState, useRef, useEffect } from "react";
import { Mic, Square, Pause, Volume2, Sparkles, Activity, Globe, User } from "lucide-react";
import { api } from "../services/api";
import { VoiceItem } from "../types";

interface Props {
  voices: VoiceItem[];
}

export const VoiceStudio: React.FC<Props> = ({ voices }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [status, setStatus] = useState<"idle" | "listening" | "transcribing" | "thinking" | "speaking">("idle");
  const [language, setLanguage] = useState<string>("auto");
  const [selectedVoice, setSelectedVoice] = useState<string>("ta_vani");
  const [inputText, setInputText] = useState("");
  const [messages, setMessages] = useState<Array<{ role: "user" | "assistant"; text: string; audioUrl?: string; meta?: any }>>([
    {
      role: "assistant",
      text: "Hello! I am XyraSpeech. You can speak to me in Tamil (தமிழ்), English, or mixed Tamil-English!",
    },
  ]);
  const [activeAudio, setActiveAudio] = useState<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [latestMetrics, setLatestMetrics] = useState<{ stt_ms?: number; brain_ms?: number; tts_ms?: number; total_ms?: number } | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Start microphone recording
  const startRecording = async () => {
    try {
      // Stop current playback if barge-in
      if (activeAudio) {
        activeAudio.pause();
        setIsPlaying(false);
      }

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
        await processRecordedAudio(audioBlob);
      };

      mediaRecorder.start(250);
      setIsRecording(true);
      setStatus("listening");
    } catch (err) {
      alert("Microphone access denied or unavailable.");
      setStatus("idle");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setStatus("transcribing");
    }
  };

  const processRecordedAudio = async (audioBlob: Blob) => {
    try {
      setStatus("transcribing");
      const sttStart = performance.now();
      const sttResult = await api.transcribeAudio(audioBlob, language === "auto" ? undefined : language);
      const sttElapsed = performance.now() - sttStart;

      if (!sttResult.text.trim()) {
        setStatus("idle");
        return;
      }

      // Add user turn
      setMessages((prev) => [...prev, { role: "user", text: sttResult.text }]);
      setStatus("thinking");

      // Send to XyraBrain Conversation Engine
      const res = await api.sendConversationMessage({
        text: sttResult.text,
        language: sttResult.language,
        voice_id: selectedVoice,
      });

      setLatestMetrics({
        stt_ms: Math.round(sttElapsed),
        brain_ms: res.latency_metrics.brain_ms,
        tts_ms: res.latency_metrics.tts_first_audio_ms,
        total_ms: Math.round(sttElapsed + res.latency_metrics.total_ms),
      });

      // Handle assistant audio
      let audioUrl: string | undefined;
      if (res.audio_base64) {
        audioUrl = `data:audio/wav;base64,${res.audio_base64}`;
        playAudio(audioUrl);
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: res.response_text,
          audioUrl,
          meta: res.speech_direction,
        },
      ]);
    } catch (err: any) {
      alert(`Error: ${err.message || "Failed to process audio"}`);
      setStatus("idle");
    }
  };

  const handleSendText = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputText.trim()) return;

    const textToSend = inputText.trim();
    setInputText("");
    setMessages((prev) => [...prev, { role: "user", text: textToSend }]);
    setStatus("thinking");

    try {
      const res = await api.sendConversationMessage({
        text: textToSend,
        language: language === "auto" ? undefined : language,
        voice_id: selectedVoice,
      });

      setLatestMetrics({
        brain_ms: res.latency_metrics.brain_ms,
        tts_ms: res.latency_metrics.tts_first_audio_ms,
        total_ms: res.latency_metrics.total_ms,
      });

      let audioUrl: string | undefined;
      if (res.audio_base64) {
        audioUrl = `data:audio/wav;base64,${res.audio_base64}`;
        playAudio(audioUrl);
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: res.response_text,
          audioUrl,
          meta: res.speech_direction,
        },
      ]);
    } catch (err: any) {
      alert(`Error: ${err.message}`);
      setStatus("idle");
    }
  };

  const playAudio = (url: string) => {
    if (activeAudio) activeAudio.pause();
    const audio = new Audio(url);
    setActiveAudio(audio);
    setIsPlaying(true);
    setStatus("speaking");

    audio.onended = () => {
      setIsPlaying(false);
      setStatus("idle");
    };
    audio.play();
  };

  const interruptSpeech = () => {
    if (activeAudio) {
      activeAudio.pause();
      setActiveAudio(null);
      setIsPlaying(false);
      setStatus("idle");
    }
  };

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: "24px" }}>
      {/* Left Chat & Live Assistant */}
      <div style={{ display: "flex", flexDirection: "column", height: "680px" }}>
        {/* Controls Bar */}
        <div className="glass-card" style={{ padding: "16px 20px", marginBottom: "16px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <Globe size={18} color="var(--accent-cyan)" />
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              style={{ background: "rgba(255,255,255,0.06)", color: "white", border: "1px solid var(--border-color)", padding: "8px 12px", borderRadius: "8px", outline: "none" }}
            >
              <option value="auto">🌐 Auto-Detect Language</option>
              <option value="ta">🇮🇳 Tamil (தமிழ்)</option>
              <option value="en">🇬🇧 English</option>
              <option value="ta-en">🔀 Tamil-English Mixed</option>
            </select>

            <select
              value={selectedVoice}
              onChange={(e) => setSelectedVoice(e.target.value)}
              style={{ background: "rgba(255,255,255,0.06)", color: "white", border: "1px solid var(--border-color)", padding: "8px 12px", borderRadius: "8px", outline: "none" }}
            >
              {voices.map((v) => (
                <option key={v.id} value={v.id}>
                  🎙️ {v.name}
                </option>
              ))}
            </select>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "1px" }}>Status:</span>
            <span
              style={{
                fontSize: "13px",
                fontWeight: 600,
                padding: "4px 10px",
                borderRadius: "12px",
                background:
                  status === "listening"
                    ? "rgba(244,63,94,0.2)"
                    : status === "thinking"
                    ? "rgba(245,158,11,0.2)"
                    : status === "speaking"
                    ? "rgba(16,185,129,0.2)"
                    : "rgba(255,255,255,0.08)",
                color:
                  status === "listening"
                    ? "var(--accent-rose)"
                    : status === "thinking"
                    ? "var(--accent-amber)"
                    : status === "speaking"
                    ? "var(--accent-emerald)"
                    : "var(--text-secondary)",
              }}
            >
              ● {status.toUpperCase()}
            </span>
          </div>
        </div>

        {/* Message Feed */}
        <div className="glass-card" style={{ flex: 1, padding: "20px", overflowY: "auto", display: "flex", flexDirection: "column", gap: "16px", marginBottom: "16px" }}>
          {messages.map((m, idx) => (
            <div
              key={idx}
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: m.role === "user" ? "flex-end" : "flex-start",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "4px", fontSize: "12px", color: "var(--text-muted)" }}>
                {m.role === "user" ? <User size={14} /> : <Sparkles size={14} color="var(--accent-cyan)" />}
                <span>{m.role === "user" ? "You" : "XyraSpeech"}</span>
              </div>

              <div
                style={{
                  maxWidth: "80%",
                  padding: "14px 18px",
                  borderRadius: m.role === "user" ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
                  background: m.role === "user" ? "linear-gradient(135deg, var(--accent-indigo), #4338ca)" : "rgba(255,255,255,0.06)",
                  color: "white",
                  lineHeight: "1.5",
                  fontSize: "15px",
                  border: m.role === "assistant" ? "1px solid var(--border-color)" : "none",
                }}
              >
                <div className="tamil-text">{m.text}</div>

                {m.audioUrl && (
                  <div style={{ marginTop: "10px", display: "flex", alignItems: "center", gap: "10px" }}>
                    <button
                      onClick={() => playAudio(m.audioUrl!)}
                      style={{
                        background: "rgba(255,255,255,0.15)",
                        border: "none",
                        color: "white",
                        padding: "6px 12px",
                        borderRadius: "8px",
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                        fontSize: "12px",
                        fontWeight: 600,
                      }}
                    >
                      <Volume2 size={14} /> Replay
                    </button>
                    {m.meta && (
                      <span style={{ fontSize: "11px", color: "var(--accent-cyan)" }}>
                        🎭 {m.meta.overall_emotion} • ⚡ {m.meta.segments?.[0]?.energy || 0.6}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={chatBottomRef} />
        </div>

        {/* Input Controls */}
        <div className="glass-card" style={{ padding: "16px", display: "flex", alignItems: "center", gap: "12px" }}>
          {/* Microphone Record Button */}
          <button
            onClick={isRecording ? stopRecording : startRecording}
            style={{
              width: "52px",
              height: "52px",
              borderRadius: "50%",
              border: "none",
              background: isRecording ? "var(--accent-rose)" : "linear-gradient(135deg, var(--accent-cyan), var(--accent-indigo))",
              color: "white",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
              transition: "transform 0.2s ease",
            }}
            className={isRecording ? "pulse-anim" : ""}
            title={isRecording ? "Click to stop recording" : "Click to speak"}
          >
            {isRecording ? <Square size={20} fill="white" /> : <Mic size={24} />}
          </button>

          {/* Barge-in Interruption Button */}
          {isPlaying && (
            <button
              onClick={interruptSpeech}
              style={{
                padding: "10px 16px",
                background: "rgba(244,63,94,0.2)",
                color: "var(--accent-rose)",
                border: "1px solid var(--accent-rose)",
                borderRadius: "10px",
                cursor: "pointer",
                fontWeight: 600,
                fontSize: "13px",
                display: "flex",
                alignItems: "center",
                gap: "6px",
              }}
            >
              <Pause size={14} /> Interrupt (Barge-in)
            </button>
          )}

          {/* Text Input */}
          <form onSubmit={handleSendText} style={{ flex: 1, display: "flex", gap: "10px" }}>
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Type message or click mic to speak..."
              style={{
                flex: 1,
                background: "rgba(255,255,255,0.06)",
                border: "1px solid var(--border-color)",
                padding: "14px 18px",
                borderRadius: "12px",
                color: "white",
                fontSize: "15px",
                outline: "none",
              }}
            />
            <button
              type="submit"
              style={{
                padding: "12px 24px",
                background: "linear-gradient(135deg, var(--accent-cyan), var(--accent-indigo))",
                border: "none",
                borderRadius: "12px",
                color: "white",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              Send
            </button>
          </form>
        </div>
      </div>

      {/* Right Telemetry & Cognitive Dashboard */}
      <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        {/* Latency & Telemetry */}
        <div className="glass-card" style={{ padding: "20px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "16px" }}>
            <Activity size={18} color="var(--accent-cyan)" />
            <h3 style={{ fontSize: "16px", fontWeight: 700 }}>Real-Time Telemetry</h3>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px" }}>
              <span style={{ color: "var(--text-secondary)" }}>STT Latency:</span>
              <span style={{ fontWeight: 600, color: "var(--accent-cyan)" }}>{latestMetrics?.stt_ms || "--"} ms</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px" }}>
              <span style={{ color: "var(--text-secondary)" }}>Brain Intelligence:</span>
              <span style={{ fontWeight: 600, color: "var(--accent-indigo)" }}>{latestMetrics?.brain_ms || "--"} ms</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px" }}>
              <span style={{ color: "var(--text-secondary)" }}>TTS First-Audio:</span>
              <span style={{ fontWeight: 600, color: "var(--accent-emerald)" }}>{latestMetrics?.tts_ms || "--"} ms</span>
            </div>
            <div style={{ borderTop: "1px solid var(--border-color)", paddingTop: "10px", display: "flex", justifyContent: "space-between", fontSize: "14px", fontWeight: 700 }}>
              <span>Total Turn Latency:</span>
              <span style={{ color: "var(--accent-purple)" }}>{latestMetrics?.total_ms || "--"} ms</span>
            </div>
          </div>
        </div>

        {/* Cognitive Speech Direction Card */}
        <div className="glass-card" style={{ padding: "20px", flex: 1 }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "16px" }}>
            <Sparkles size={18} color="var(--accent-indigo)" />
            <h3 style={{ fontSize: "16px", fontWeight: 700 }}>Cognitive Direction</h3>
          </div>

          {messages[messages.length - 1]?.meta ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "14px", fontSize: "13px" }}>
              <div>
                <span style={{ color: "var(--text-muted)", fontSize: "12px" }}>Detected Emotion:</span>
                <div style={{ fontWeight: 700, fontSize: "16px", color: "var(--accent-amber)", marginTop: "2px" }}>
                  {messages[messages.length - 1].meta.overall_emotion.toUpperCase()}
                </div>
              </div>

              <div>
                <span style={{ color: "var(--text-muted)", fontSize: "12px" }}>Speaking Delivery Style:</span>
                <div style={{ fontWeight: 600, color: "white", marginTop: "2px" }}>
                  {messages[messages.length - 1].meta.overall_style}
                </div>
              </div>

              <div>
                <span style={{ color: "var(--text-muted)", fontSize: "12px" }}>Speech Energy:</span>
                <div style={{ width: "100%", height: "8px", background: "rgba(255,255,255,0.1)", borderRadius: "4px", marginTop: "4px", overflow: "hidden" }}>
                  <div
                    style={{
                      height: "100%",
                      width: `${(messages[messages.length - 1].meta.segments?.[0]?.energy || 0.6) * 100}%`,
                      background: "linear-gradient(90deg, var(--accent-cyan), var(--accent-indigo))",
                    }}
                  />
                </div>
              </div>

              <div>
                <span style={{ color: "var(--text-muted)", fontSize: "12px" }}>Rate / Pitch:</span>
                <div style={{ fontWeight: 600, color: "white", marginTop: "2px" }}>
                  {messages[messages.length - 1].meta.segments?.[0]?.speed || 1.0}x Speed • {messages[messages.length - 1].meta.segments?.[0]?.pitch || 1.0}x Pitch
                </div>
              </div>
            </div>
          ) : (
            <div style={{ color: "var(--text-muted)", fontSize: "13px", lineHeight: "1.6" }}>
              Speak or send a message to observe real-time speech performance parameters and prosody planning.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
