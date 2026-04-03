import { AnimatePresence, motion } from "motion/react";
import type { FeedEvent } from "../../types/society";

interface SocietyFeedProps {
  events: FeedEvent[];
}

const TRIBE_COLORS = {
  image: "#2ea36a",
  text: "#c08a3a",
  audio: "#3b82b8",
};

function formatTime(date: Date): string {
  return date.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

function FeedEventItem({ event }: { event: FeedEvent }) {
  const tribeColor = event.tribe ? TRIBE_COLORS[event.tribe] : "#f59e0b";

  if (event.type === "oracle_proclamation") {
    return (
      <div
        className="mx-[-6px] px-4 py-3 font-mono"
        style={{
          backgroundColor: "rgba(245,158,11,0.12)",
          borderLeft: "3px solid #f59e0b",
          borderTop: "1px solid rgba(245,158,11,0.25)",
          borderBottom: "1px solid rgba(245,158,11,0.25)",
        }}
      >
        <div className="flex items-center gap-2 mb-1.5">
          <span style={{ color: "#f59e0b" }}>⚡</span>
          <span
            className="text-[9px] uppercase tracking-widest font-bold"
            style={{ color: "#f59e0b99" }}
          >
            ORACLE PROCLAMATION · {formatTime(event.timestamp)}
          </span>
        </div>
        <p
          className="text-[11px] uppercase tracking-wide leading-snug font-bold"
          style={{ color: "#f2a23a" }}
        >
          {event.message}
        </p>
      </div>
    );
  }

  if (event.type === "agent_death") {
    return (
      <div
        className="p-2 rounded-sm text-[11px] font-mono"
        style={{
          backgroundColor: "rgba(239,68,68,0.06)",
          border: "1px solid rgba(239,68,68,0.25)",
        }}
      >
        <div className="flex items-center gap-1.5 mb-1">
          <span>💀</span>
          <span
            className="text-[9px] uppercase tracking-wider"
            style={{ color: "#ef444488" }}
          >
            DEATH · {formatTime(event.timestamp)}
          </span>
        </div>
        <p style={{ color: "#ef4444" }} className="text-[10px]">
          {event.message}
        </p>
      </div>
    );
  }

  if (event.type === "agent_born") {
    return (
      <div
        className="p-2 rounded-sm text-[11px] font-mono"
        style={{
          backgroundColor: "rgba(34,197,94,0.06)",
          border: "1px solid rgba(34,197,94,0.25)",
        }}
      >
        <div className="flex items-center gap-1.5 mb-1">
          <span>🌱</span>
          <span
            className="text-[9px] uppercase tracking-wider"
            style={{ color: "#22c55e88" }}
          >
            BIRTH · {formatTime(event.timestamp)}
          </span>
        </div>
        <p style={{ color: "#22c55e" }} className="text-[10px]">
          {event.message}
        </p>
      </div>
    );
  }

  if (event.type === "task_completed") {
    const delta = event.healthDelta ?? 0;
    const deltaColor = delta >= 0 ? "#22c55e" : "#ef4444";
    const deltaStr = delta >= 0 ? `+${delta}` : `${delta}`;
    return (
      <div
        className="p-2 rounded-sm text-[11px] font-mono"
        style={{
          backgroundColor: `${tribeColor}0a`,
          border: `1px solid ${tribeColor}30`,
        }}
      >
        <div className="flex items-center justify-between gap-1.5 mb-1">
          <div className="flex items-center gap-1.5">
            <span
              className="text-[9px] font-bold"
              style={{ color: tribeColor }}
            >
              {event.agentName}
            </span>
            <span
              className="text-[9px] uppercase tracking-wider"
              style={{ color: "#55555588" }}
            >
              TASK · {formatTime(event.timestamp)}
            </span>
          </div>
          <span
            className="text-[9px] font-bold tabular-nums"
            style={{ color: deltaColor }}
          >
            {deltaStr} HP
          </span>
        </div>
        <p style={{ color: "#a3a3a3" }} className="text-[10px] truncate">
          {event.message}
        </p>
      </div>
    );
  }

  // agent_message — speech bubble
  return (
    <div
      className="p-2 rounded-sm text-[11px] font-mono"
      style={{
        backgroundColor: `${tribeColor}08`,
        border: `1px solid ${tribeColor}28`,
        borderLeft: `2px solid ${tribeColor}`,
      }}
    >
      <div className="flex items-center gap-1.5 mb-1">
        <span className="text-[9px] font-bold" style={{ color: tribeColor }}>
          {event.agentName}
        </span>
        <span
          className="text-[9px] uppercase tracking-wider"
          style={{ color: "#55555588" }}
        >
          MSG · {formatTime(event.timestamp)}
        </span>
      </div>
      <p style={{ color: "#888" }} className="text-[10px] italic">
        {event.message}
      </p>
    </div>
  );
}

export function SocietyFeed({ events }: SocietyFeedProps) {
  return (
    <div
      className="flex flex-col h-full rounded-sm overflow-hidden"
      style={{
        border: "1px solid #222",
        backgroundColor: "#0e0e0e",
        minWidth: 280,
        maxWidth: 340,
        width: "100%",
      }}
    >
      {/* Header */}
      <div
        className="px-3 py-2.5 flex items-center justify-between flex-shrink-0"
        style={{ borderBottom: "1px solid #222" }}
      >
        <span
          className="text-xs font-mono font-bold uppercase tracking-widest"
          style={{ color: "#555" }}
        >
          SOCIETY EVENT FEED
        </span>
        <span
          className="text-[9px] font-mono px-1.5 py-0.5 rounded-sm"
          style={{
            color: "#333",
            backgroundColor: "#1a1a1a",
            border: "1px solid #222",
          }}
        >
          {events.length}/50
        </span>
      </div>

      {/* Feed */}
      <div className="flex flex-col gap-1.5 p-1.5 overflow-y-auto flex-1">
        <AnimatePresence initial={false}>
          {events.length === 0 ? (
            <div
              data-ocid="feed.empty_state"
              className="flex items-center justify-center h-20 text-[11px] font-mono"
              style={{ color: "#333" }}
            >
              NO EVENTS YET...
            </div>
          ) : (
            events.map((event) => (
              <motion.div
                key={event.id}
                data-ocid="feed.item.1"
                initial={{ opacity: 0, y: -10, scale: 0.97 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.25 }}
              >
                <FeedEventItem event={event} />
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
