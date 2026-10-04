import React, { useState, useEffect } from "react";
import { Mic2, MessageSquare, Volume2, Globe2, Layers, Cpu } from "lucide-react";
import { VoiceStudio } from "./components/VoiceStudio";
import { TextToSpeechStudio } from "./components/TextToSpeechStudio";
import { SpeechToTextStudio } from "./components/SpeechToTextStudio";
import { Translator } from "./components/Translator";
import { VoiceLibrary } from "./components/VoiceLibrary";
import { SystemStatus } from "./components/SystemStatus";
import { api } from "./services/api";
import { VoiceItem } from "./types";

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"assistant" | "tts" | "stt" | "translator" | "voices" | "status">("assistant");
  const [voices, setVoices] = useState<VoiceItem[]>([]);

  const refreshVoices = () => {
    api.getVoices().then(setVoices).catch(console.error);
  };

  useEffect(() => {
    refreshVoices();
  }, []);

  return (
    <div style={{ maxWidth: "1340px", margin: "0 auto", padding: "24px 20px" }}>
      {/* Header */}
      <header
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "28px",
          padding: "16px 24px",
          background: "rgba(15, 23, 42, 0.65)",
          backdropFilter: "blur(20px)",
          borderRadius: "20px",
          border: "1px solid rgba(255, 255, 255, 0.12)",
          boxShadow: "0 10px 30px rgba(0,0,0,0.4)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
          <div
            className="pulse-anim"
            style={{
              width: "48px",
              height: "48px",
              borderRadius: "14px",
              background: "linear-gradient(135deg, #06b6d4, #6366f1, #a855f7)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "white",
              boxShadow: "0 0 24px rgba(99, 102, 241, 0.6)",
            }}
          >
            <Mic2 size={26} />
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <h1 style={{ fontSize: "24px", fontWeight: 900, fontFamily: "var(--font-heading)" }}>
                Xyra<span className="gradient-text">Speech</span> Studio
              </h1>
              <span
                style={{
                  fontSize: "10px",
                  background: "rgba(6, 182, 212, 0.15)",
                  color: "var(--accent-cyan)",
                  border: "1px solid rgba(6, 182, 212, 0.4)",
                  padding: "2px 8px",
                  borderRadius: "12px",
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.5px",
                }}
              >
                v1.0 • Voice Clone AI
              </span>
            </div>
            <p style={{ fontSize: "12px", color: "var(--text-secondary)", fontWeight: 500, marginTop: "2px" }}>
              Local-First Cognitive Speech Intelligence & Zero-Shot Voice Cloning • Tamil (`ta`) & English (`en`)
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav
          style={{
            display: "flex",
            gap: "6px",
            background: "rgba(0,0,0,0.35)",
            padding: "6px",
            borderRadius: "14px",
            border: "1px solid rgba(255,255,255,0.08)",
          }}
        >
          <TabButton active={activeTab === "assistant"} onClick={() => setActiveTab("assistant")} icon={<MessageSquare size={16} />} label="Voice Assistant" />
          <TabButton active={activeTab === "tts"} onClick={() => setActiveTab("tts")} icon={<Volume2 size={16} />} label="Text-to-Speech" />
          <TabButton active={activeTab === "stt"} onClick={() => setActiveTab("stt")} icon={<Mic2 size={16} />} label="Speech-to-Text" />
          <TabButton active={activeTab === "translator"} onClick={() => setActiveTab("translator")} icon={<Globe2 size={16} />} label="Translator" />
          <TabButton active={activeTab === "voices"} onClick={() => setActiveTab("voices")} icon={<Layers size={16} />} label="Voice Library" />
          <TabButton active={activeTab === "status"} onClick={() => setActiveTab("status")} icon={<Cpu size={16} />} label="System" />
        </nav>
      </header>

      {/* Main Content Area */}
      <main>
        {activeTab === "assistant" && <VoiceStudio voices={voices} />}
        {activeTab === "tts" && <TextToSpeechStudio voices={voices} />}
        {activeTab === "stt" && <SpeechToTextStudio />}
        {activeTab === "translator" && <Translator />}
        {activeTab === "voices" && <VoiceLibrary voices={voices} onVoicesUpdated={refreshVoices} />}
        {activeTab === "status" && <SystemStatus />}
      </main>
    </div>
  );
};

interface TabProps {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
}

const TabButton: React.FC<TabProps> = ({ active, onClick, icon, label }) => (
  <button
    onClick={onClick}
    style={{
      padding: "8px 16px",
      borderRadius: "8px",
      border: "none",
      background: active ? "linear-gradient(135deg, var(--accent-cyan), var(--accent-indigo))" : "transparent",
      color: active ? "white" : "var(--text-secondary)",
      fontWeight: 600,
      fontSize: "13px",
      cursor: "pointer",
      display: "flex",
      alignItems: "center",
      gap: "6px",
      transition: "all 0.2s ease",
    }}
  >
    {icon} {label}
  </button>
);
