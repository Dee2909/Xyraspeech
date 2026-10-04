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

  useEffect(() => {
    api.getVoices().then(setVoices).catch(console.error);
  }, []);

  return (
    <div style={{ maxWidth: "1280px", margin: "0 auto", padding: "24px 20px" }}>
      {/* Header */}
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "28px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div
            style={{
              width: "44px",
              height: "44px",
              borderRadius: "12px",
              background: "linear-gradient(135deg, var(--accent-cyan), var(--accent-indigo))",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "white",
            }}
          >
            <Mic2 size={24} />
          </div>
          <div>
            <h1 style={{ fontSize: "22px", fontWeight: 800, letterSpacing: "-0.5px" }}>
              Xyra<span style={{ color: "var(--accent-cyan)" }}>Speech</span> Studio
            </h1>
            <p style={{ fontSize: "12px", color: "var(--text-muted)", fontWeight: 500 }}>
              Local-First Real-Time Multilingual Speech Platform • Tamil & English
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{ display: "flex", gap: "8px", background: "rgba(255,255,255,0.04)", padding: "6px", borderRadius: "12px", border: "1px solid var(--border-color)" }}>
          <TabButton active={activeTab === "assistant"} onClick={() => setActiveTab("assistant")} icon={<MessageSquare size={16} />} label="Voice Assistant" />
          <TabButton active={activeTab === "tts"} onClick={() => setActiveTab("tts")} icon={<Volume2 size={16} />} label="Text-to-Speech" />
          <TabButton active={activeTab === "stt"} onClick={() => setActiveTab("stt")} icon={<Mic2 size={16} />} label="Speech-to-Text" />
          <TabButton active={activeTab === "translator"} onClick={() => setActiveTab("translator")} icon={<Globe2 size={16} />} label="Translator" />
          <TabButton active={activeTab === "voices"} onClick={() => setActiveTab("voices")} icon={<Layers size={16} />} label="Voices" />
          <TabButton active={activeTab === "status"} onClick={() => setActiveTab("status")} icon={<Cpu size={16} />} label="System" />
        </nav>
      </header>

      {/* Main Content Area */}
      <main>
        {activeTab === "assistant" && <VoiceStudio voices={voices} />}
        {activeTab === "tts" && <TextToSpeechStudio voices={voices} />}
        {activeTab === "stt" && <SpeechToTextStudio />}
        {activeTab === "translator" && <Translator />}
        {activeTab === "voices" && <VoiceLibrary voices={voices} />}
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
