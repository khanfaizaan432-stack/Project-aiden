import { useNavigate, useParams } from "@tanstack/react-router";
import { motion } from "motion/react";
import { useMemo } from "react";
import { HealthBar } from "../components/society/HealthBar";
import { PixelSprite } from "../components/society/PixelSprite";
import { StateBadge } from "../components/society/StateBadge";
import { INITIAL_AGENTS } from "../data/initialAgents";

const TRIBE_BORDER: Record<string, string> = {
  image: "#2a6642",
  text: "#6b4c1e",
  audio: "#1e4a6e",
};

const TRIBE_GLOW: Record<string, string> = {
  image: "rgba(46,163,106,0.15)",
  text: "rgba(192,138,58,0.15)",
  audio: "rgba(59,130,184,0.15)",
};

const MODALITY_LABEL: Record<string, string> = {
  image: "IMG",
  text: "TXT",
  audio: "AUD",
};

// Mock task history generator
function generateTaskHistory(agentId: number, agentName: string, tribe: string) {
  const tasks = [
    "Processed complex visual analysis",
    "Generated high-fidelity output",
    "Analyzed pattern recognition data",
    "Synthesized creative content",
    "Executed collaborative task",
    "Optimized performance metrics",
    "Completed knowledge integration",
    "Performed system diagnostics",
    "Enhanced neural pathways",
    "Refined skill parameters",
  ];
  
  const now = Date.now();
  return Array.from({ length: 10 }, (_, i) => ({
    id: `task-${agentId}-${i}`,
    task: tasks[i % tasks.length],
    timestamp: new Date(now - i * 3600000), // Each task 1 hour older than previous
    success: Math.random() > 0.2,
    healthDelta: Math.random() > 0.2 ? Math.floor(Math.random() * 5) + 1 : -Math.floor(Math.random() * 8) - 2,
  }));
}

// Mock memory insights generator
function generateMemoryInsights(agentId: number) {
  const insights = [
    {
      id: `mem-${agentId}-1`,
      reasoning: "Successfully collaborated with tribe members on multi-agent task requiring synchronized outputs and shared context.",
      confidence: 0.92,
    },
    {
      id: `mem-${agentId}-2`,
      reasoning: "Learned optimal parameter adjustments when processing high-complexity inputs under resource constraints.",
      confidence: 0.87,
    },
    {
      id: `mem-${agentId}-3`,
      reasoning: "Discovered effective recovery patterns after experiencing confusion state, improving resilience metrics.",
      confidence: 0.79,
    },
  ];
  
  return insights;
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

export function AgentDetail() {
  const navigate = useNavigate();
  const params = useParams({ strict: false }) as { id?: string };
  const agentId = params.id ? Number.parseInt(params.id, 10) : undefined;
  
  const agent = useMemo(() => {
    if (!agentId) return null;
    return INITIAL_AGENTS.find((a) => a.id === agentId);
  }, [agentId]);

  const taskHistory = useMemo(() => {
    if (!agent) return [];
    return generateTaskHistory(agent.id, agent.name, agent.tribe);
  }, [agent]);

  const memoryInsights = useMemo(() => {
    if (!agent) return [];
    return generateMemoryInsights(agent.id);
  }, [agent]);

  // Agent not found
  if (!agent) {
    return (
      <div
        className="min-h-screen flex flex-col items-center justify-center font-mono"
        style={{ backgroundColor: "#0a0a0a" }}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
          className="p-8 rounded-sm text-center"
          style={{ border: "1px solid #2a2a2a", backgroundColor: "#101010" }}
        >
          <div className="text-4xl mb-4">⚠</div>
          <h1
            className="text-2xl font-black uppercase tracking-widest mb-6"
            style={{ color: "#f59e0b" }}
          >
            AGENT NOT FOUND
          </h1>
          <button
            data-ocid="agent_detail.back_button"
            type="button"
            onClick={() => navigate({ to: "/" })}
            className="px-4 py-2 text-xs font-mono uppercase tracking-widest rounded-sm transition-all"
            style={{
              border: "1px solid #2a6642",
              color: "#2ea36a",
              backgroundColor: "transparent",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = "rgba(46,163,106,0.1)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "transparent";
            }}
          >
            ← BACK TO SOCIETY
          </button>
        </motion.div>
      </div>
    );
  }

  const borderColor = TRIBE_BORDER[agent.tribe];
  const glowColor = TRIBE_GLOW[agent.tribe];
  const isEgg = agent.state === "egg";
  const isDead = agent.state === "dead";
  
  // Calculate stats
  const totalTasks = taskHistory.length;
  const successfulTasks = taskHistory.filter((t) => t.success).length;
  const successRate = totalTasks > 0 ? Math.round((successfulTasks / totalTasks) * 100) : 0;
  const avgConfidence = Math.round(
    memoryInsights.reduce((sum, m) => sum + m.confidence, 0) / memoryInsights.length * 100
  );

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="min-h-screen font-mono pb-8"
      style={{
        backgroundColor: "#0a0a0a",
        backgroundImage:
          "radial-gradient(ellipse at center, #0a0a0a 55%, #050505 100%)",
      }}
    >
      {/* Back button */}
      <div className="px-7 pt-6 pb-4">
        <button
          data-ocid="agent_detail.back_button"
          type="button"
          onClick={() => navigate({ to: "/" })}
          className="px-3 py-1.5 text-xs font-mono uppercase tracking-widest rounded-sm transition-all inline-flex items-center gap-2"
          style={{
            border: `1px solid ${borderColor}`,
            color: borderColor,
            backgroundColor: "transparent",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = glowColor;
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "transparent";
          }}
        >
          ← BACK
        </button>
      </div>

      {/* Main content */}
      <div className="px-7 max-w-7xl mx-auto">
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="rounded-sm p-6 mb-6"
          style={{
            backgroundColor: "#141414",
            border: `1px solid ${borderColor}`,
            boxShadow: `0 0 12px ${glowColor}`,
          }}
        >
          {/* Header section */}
          <div className="flex items-start gap-6 mb-6">
            {/* Large sprite */}
            <div className="flex-shrink-0">
              <PixelSprite
                agentId={agent.id}
                tribe={agent.tribe}
                size={80}
                isDead={isDead}
                isEgg={isEgg}
              />
            </div>

            {/* Name and badges */}
            <div className="flex-1">
              <h1
                className="text-3xl font-mono font-black uppercase tracking-wider mb-3"
                style={{
                  color: "#f59e0b",
                  textDecoration: isDead ? "line-through" : "none",
                }}
              >
                {agent.name}
              </h1>
              
              <div className="flex items-center gap-2 mb-4">
                <StateBadge state={agent.state} />
                <span
                  className="text-xs font-mono font-bold uppercase px-2 py-1 rounded-sm"
                  style={{
                    color: borderColor,
                    backgroundColor: `${borderColor}20`,
                    border: `1px solid ${borderColor}40`,
                  }}
                >
                  {MODALITY_LABEL[agent.tribe]} TRIBE
                </span>
              </div>

              {/* Health bar */}
              {!isEgg && (
                <div className="mb-4">
                  <HealthBar health={agent.health} showValue={true} />
                </div>
              )}

              {/* Stats boxes */}
              <div className="grid grid-cols-4 gap-3">
                <div
                  className="p-3 rounded-sm"
                  style={{
                    backgroundColor: "#0e0e0e",
                    border: "1px solid #222",
                  }}
                >
                  <div
                    className="text-xs font-mono uppercase tracking-wider mb-1"
                    style={{ color: "#555" }}
                  >
                    Tasks
                  </div>
                  <div
                    className="text-2xl font-mono font-bold"
                    style={{ color: "#e7e7e7" }}
                  >
                    {totalTasks}
                  </div>
                </div>

                <div
                  className="p-3 rounded-sm"
                  style={{
                    backgroundColor: "#0e0e0e",
                    border: "1px solid #222",
                  }}
                >
                  <div
                    className="text-xs font-mono uppercase tracking-wider mb-1"
                    style={{ color: "#555" }}
                  >
                    Success
                  </div>
                  <div
                    className="text-2xl font-mono font-bold"
                    style={{ color: "#22c55e" }}
                  >
                    {successRate}%
                  </div>
                </div>

                <div
                  className="p-3 rounded-sm"
                  style={{
                    backgroundColor: "#0e0e0e",
                    border: "1px solid #222",
                  }}
                >
                  <div
                    className="text-xs font-mono uppercase tracking-wider mb-1"
                    style={{ color: "#555" }}
                  >
                    Confidence
                  </div>
                  <div
                    className="text-2xl font-mono font-bold"
                    style={{ color: "#f59e0b" }}
                  >
                    {avgConfidence}%
                  </div>
                </div>

                <div
                  className="p-3 rounded-sm"
                  style={{
                    backgroundColor: "#0e0e0e",
                    border: "1px solid #222",
                  }}
                >
                  <div
                    className="text-xs font-mono uppercase tracking-wider mb-1"
                    style={{ color: "#555" }}
                  >
                    Health
                  </div>
                  <div
                    className="text-2xl font-mono font-bold"
                    style={{
                      color:
                        agent.health > 60
                          ? "#00ff88"
                          : agent.health > 30
                            ? "#f59e0b"
                            : "#ef4444",
                    }}
                  >
                    {agent.health}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Personality */}
          <div
            className="p-4 rounded-sm italic"
            style={{
              backgroundColor: "#0e0e0e",
              border: "1px solid #222",
              color: "#888",
            }}
          >
            "{agent.personality}"
          </div>
        </motion.div>

        {/* Two column layout */}
        <div className="grid grid-cols-2 gap-6">
          {/* LEFT: Task history */}
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="rounded-sm overflow-hidden"
            style={{
              backgroundColor: "#0e0e0e",
              border: "1px solid #222",
            }}
          >
            {/* Header */}
            <div
              className="px-4 py-3 flex items-center justify-between"
              style={{ borderBottom: "1px solid #222" }}
            >
              <span
                className="text-xs font-mono font-bold uppercase tracking-widest"
                style={{ color: "#555" }}
              >
                TASK HISTORY
              </span>
              <span
                className="text-[9px] font-mono px-1.5 py-0.5 rounded-sm"
                style={{
                  color: "#333",
                  backgroundColor: "#1a1a1a",
                  border: "1px solid #222",
                }}
              >
                {taskHistory.length}
              </span>
            </div>

            {/* Task feed */}
            <div className="p-3 space-y-2 max-h-[600px] overflow-y-auto">
              {taskHistory.map((task) => {
                const deltaColor = task.healthDelta >= 0 ? "#22c55e" : "#ef4444";
                const deltaStr =
                  task.healthDelta >= 0
                    ? `+${task.healthDelta}`
                    : `${task.healthDelta}`;

                return (
                  <div
                    key={task.id}
                    className="p-2.5 rounded-sm text-[11px] font-mono"
                    style={{
                      backgroundColor: task.success
                        ? `${borderColor}0a`
                        : "rgba(239,68,68,0.06)",
                      border: task.success
                        ? `1px solid ${borderColor}30`
                        : "1px solid rgba(239,68,68,0.25)",
                    }}
                  >
                    <div className="flex items-center justify-between gap-2 mb-1">
                      <span
                        className="text-[9px] uppercase tracking-wider"
                        style={{ color: "#55555588" }}
                      >
                        {formatTime(task.timestamp)}
                      </span>
                      <span
                        className="text-[9px] font-bold tabular-nums"
                        style={{ color: deltaColor }}
                      >
                        {deltaStr} HP
                      </span>
                    </div>
                    <p
                      style={{ color: task.success ? "#a3a3a3" : "#ef4444" }}
                      className="text-[10px]"
                    >
                      {task.success ? "✓" : "✗"} {task.task}
                    </p>
                  </div>
                );
              })}
            </div>
          </motion.div>

          {/* RIGHT: Memory insights */}
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="rounded-sm overflow-hidden"
            style={{
              backgroundColor: "#0e0e0e",
              border: "1px solid #222",
            }}
          >
            {/* Header */}
            <div
              className="px-4 py-3"
              style={{ borderBottom: "1px solid #222" }}
            >
              <span
                className="text-xs font-mono font-bold uppercase tracking-widest"
                style={{ color: "#555" }}
              >
                MEMORY INSIGHTS
              </span>
            </div>

            {/* Memory cards */}
            <div className="p-3 space-y-3">
              {memoryInsights.map((insight) => (
                <div
                  key={insight.id}
                  className="p-3 rounded-sm"
                  style={{
                    backgroundColor: "#141414",
                    border: "1px solid #2a2a2a",
                  }}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span
                      className="text-[9px] font-mono font-bold uppercase tracking-wider"
                      style={{ color: "#555" }}
                    >
                      RECALLED MEMORY
                    </span>
                    <span
                      className="text-[10px] font-mono font-bold tabular-nums"
                      style={{
                        color:
                          insight.confidence > 0.85
                            ? "#22c55e"
                            : insight.confidence > 0.7
                              ? "#f59e0b"
                              : "#ef4444",
                      }}
                    >
                      {Math.round(insight.confidence * 100)}%
                    </span>
                  </div>
                  <p
                    className="text-xs font-mono leading-relaxed"
                    style={{ color: "#888" }}
                  >
                    {insight.reasoning}
                  </p>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}
