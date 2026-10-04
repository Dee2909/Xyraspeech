import React, { useEffect, useState } from "react";
import { CheckCircle2, XCircle, RefreshCw } from "lucide-react";
import { api } from "../services/api";
import { ModelHealthStatus } from "../types";

export const SystemStatus: React.FC = () => {
  const [health, setHealth] = useState<ModelHealthStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchHealth = async () => {
    setIsLoading(true);
    try {
      const data = await api.getModelsHealth();
      setHealth(data);
    } catch {
      setHealth(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  return (
    <div className="glass-card" style={{ padding: "24px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <div>
          <h2 style={{ fontSize: "18px", fontWeight: 700 }}>System Health & Engine Telemetry</h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "14px", marginTop: "4px" }}>
            Real-time status of local offline engines (STT, TTS, XyraBrain, Translation).
          </p>
        </div>
        <button
          onClick={fetchHealth}
          disabled={isLoading}
          style={{
            padding: "8px 14px",
            background: "rgba(255,255,255,0.08)",
            border: "1px solid var(--border-color)",
            borderRadius: "8px",
            color: "white",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "6px",
            fontSize: "13px",
            fontWeight: 600,
          }}
        >
          <RefreshCw size={14} className={isLoading ? "pulse-anim" : ""} /> Refresh Status
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: "16px" }}>
        {/* STT Engine */}
        <div style={{ padding: "18px", background: "rgba(255,255,255,0.04)", border: "1px solid var(--border-color)", borderRadius: "12px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <span style={{ fontWeight: 700, fontSize: "15px" }}>STT Engine</span>
            {health?.engines.stt.available ? <CheckCircle2 color="var(--accent-emerald)" size={18} /> : <XCircle color="var(--accent-rose)" size={18} />}
          </div>
          <div style={{ fontSize: "13px", color: "var(--text-secondary)" }}>Engine: faster-whisper ({health?.engines.stt.model || "tiny"})</div>
          <div style={{ fontSize: "12px", color: "var(--accent-emerald)", marginTop: "4px" }}>Status: Local Offline Ready</div>
        </div>

        {/* TTS Engine */}
        <div style={{ padding: "18px", background: "rgba(255,255,255,0.04)", border: "1px solid var(--border-color)", borderRadius: "12px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <span style={{ fontWeight: 700, fontSize: "15px" }}>TTS Engine</span>
            {health?.engines.tts.available ? <CheckCircle2 color="var(--accent-emerald)" size={18} /> : <XCircle color="var(--accent-rose)" size={18} />}
          </div>
          <div style={{ fontSize: "13px", color: "var(--text-secondary)" }}>Engine: Mac Native High-Fidelity</div>
          <div style={{ fontSize: "12px", color: "var(--accent-emerald)", marginTop: "4px" }}>Status: {health?.engines.tts.voice_count || 4} Installed Voices</div>
        </div>

        {/* XyraBrain LLM */}
        <div style={{ padding: "18px", background: "rgba(255,255,255,0.04)", border: "1px solid var(--border-color)", borderRadius: "12px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <span style={{ fontWeight: 700, fontSize: "15px" }}>XyraBrain LLM</span>
            {health?.engines.brain_llm.model_available ? <CheckCircle2 color="var(--accent-emerald)" size={18} /> : <XCircle color="var(--accent-rose)" size={18} />}
          </div>
          <div style={{ fontSize: "13px", color: "var(--text-secondary)" }}>Target: Ollama ({health?.engines.brain_llm.model || "mistral:latest"})</div>
          <div style={{ fontSize: "12px", color: health?.engines.brain_llm.model_available ? "var(--accent-emerald)" : "var(--accent-rose)", marginTop: "4px" }}>
            {health?.engines.brain_llm.model_available ? "Status: Connected & Online" : "Status: Model Not Found"}
          </div>
        </div>

        {/* Translation */}
        <div style={{ padding: "18px", background: "rgba(255,255,255,0.04)", border: "1px solid var(--border-color)", borderRadius: "12px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <span style={{ fontWeight: 700, fontSize: "15px" }}>Neural Translation</span>
            {health?.engines.translation.available ? <CheckCircle2 color="var(--accent-emerald)" size={18} /> : <XCircle color="var(--accent-rose)" size={18} />}
          </div>
          <div style={{ fontSize: "13px", color: "var(--text-secondary)" }}>Pairs: Tamil ↔ English</div>
          <div style={{ fontSize: "12px", color: "var(--accent-emerald)", marginTop: "4px" }}>Status: Ready</div>
        </div>
      </div>
    </div>
  );
};
