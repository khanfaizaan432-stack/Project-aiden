import type { Agent, Modality } from "../../types/society";
import { AgentCard } from "./AgentCard";

interface TribeColumnProps {
  tribe: Modality;
  agents: Agent[];
}

const TRIBE_CONFIG: Record<
  Modality,
  { label: string; icon: string; color: string; border: string; glow: string }
> = {
  image: {
    label: "IMAGE TRIBE",
    icon: "🖼",
    color: "#2ea36a",
    border: "#2a6642",
    glow: "rgba(46,163,106,0.12)",
  },
  text: {
    label: "TEXT TRIBE",
    icon: "📝",
    color: "#c08a3a",
    border: "#6b4c1e",
    glow: "rgba(192,138,58,0.12)",
  },
  audio: {
    label: "AUDIO TRIBE",
    icon: "🔊",
    color: "#3b82b8",
    border: "#1e4a6e",
    glow: "rgba(59,130,184,0.12)",
  },
};

export function TribeColumn({ tribe, agents }: TribeColumnProps) {
  const config = TRIBE_CONFIG[tribe];
  const tribeAgents = agents.filter((a) => a.tribe === tribe);
  const activeCount = tribeAgents.filter(
    (a) => a.state !== "dead" && a.state !== "egg",
  ).length;

  return (
    <div
      className="flex flex-col rounded-sm overflow-hidden"
      style={{
        border: `1px solid ${config.border}`,
        boxShadow: `0 0 16px ${config.glow}`,
        backgroundColor: "#101010",
      }}
    >
      {/* Column header */}
      <div
        className="px-3 py-1.5 flex items-center justify-between"
        style={{
          borderBottom: `1px solid ${config.border}`,
          backgroundColor: `${config.border}22`,
        }}
      >
        <div className="flex items-center gap-2">
          <span className="text-base">{config.icon}</span>
          <span
            className="text-sm font-mono font-bold uppercase tracking-widest"
            style={{ color: config.color }}
          >
            {config.label}
          </span>
        </div>
        <div className="flex items-center gap-1">
          <span
            className="text-[10px] font-mono"
            style={{ color: config.color }}
          >
            {activeCount}/{tribeAgents.length}
          </span>
        </div>
      </div>

      {/* Agent cards */}
      <div
        className="flex flex-col gap-1 p-1 overflow-y-auto"
        style={{ maxHeight: "calc(100vh - 200px)" }}
      >
        {tribeAgents.map((agent, index) => (
          <AgentCard key={agent.id} agent={agent} index={index + 1} />
        ))}
      </div>
    </div>
  );
}
