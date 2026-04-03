import type { AgentState } from "../../types/society";

interface StateBadgeProps {
  state: AgentState;
}

const STATE_CONFIG: Record<
  AgentState,
  { label: string; color: string; bg: string }
> = {
  ascending: {
    label: "ASCENDING",
    color: "#f59e0b",
    bg: "rgba(245,158,11,0.15)",
  },
  active: { label: "ACTIVE", color: "#22c55e", bg: "rgba(34,197,94,0.12)" },
  confused: {
    label: "CONFUSED",
    color: "#f97316",
    bg: "rgba(249,115,22,0.12)",
  },
  dead: { label: "DEAD", color: "#6b7280", bg: "rgba(107,114,128,0.12)" },
  egg: { label: "EGG", color: "#8b5cf6", bg: "rgba(139,92,246,0.12)" },
  hatchling: {
    label: "HATCHLING",
    color: "#14b8a6",
    bg: "rgba(20,184,166,0.12)",
  },
};

export function StateBadge({ state }: StateBadgeProps) {
  const config = STATE_CONFIG[state];
  return (
    <span
      className="text-[10px] font-mono font-bold uppercase tracking-wider px-1.5 py-0.5 rounded-sm"
      style={{
        color: config.color,
        backgroundColor: config.bg,
        border: `1px solid ${config.color}40`,
      }}
    >
      {config.label}
    </span>
  );
}
