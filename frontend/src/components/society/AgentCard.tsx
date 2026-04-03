import { useNavigate } from "@tanstack/react-router";
import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState } from "react";
import type { Agent } from "../../types/society";
import { HealthBar } from "./HealthBar";
import { PixelSprite } from "./PixelSprite";
import { StateBadge } from "./StateBadge";

interface AgentCardProps {
  agent: Agent;
  index: number;
}

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

export function AgentCard({ agent, index }: AgentCardProps) {
  const navigate = useNavigate();
  const isEgg = agent.state === "egg";
  const isDead = agent.state === "dead";

  const borderColor = TRIBE_BORDER[agent.tribe];
  const glowColor = TRIBE_GLOW[agent.tribe];

  const [isFlashing, setIsFlashing] = useState(false);

  useEffect(() => {
    if (!agent.justDied) return;
    let count = 0;
    const interval = setInterval(() => {
      setIsFlashing((v) => !v);
      count++;
      if (count >= 6) {
        clearInterval(interval);
        setIsFlashing(false);
      }
    }, 250);
    return () => clearInterval(interval);
  }, [agent.justDied]);

  // Reset flash state when agent revives
  useEffect(() => {
    if (!isDead) {
      setIsFlashing(false);
    }
  }, [isDead]);

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={`${agent.id}-${agent.state}`}
        data-ocid={`agent.card.${index}`}
        initial={
          agent.justBorn
            ? { scale: 0, opacity: 0, filter: "blur(8px)" }
            : { opacity: 1 }
        }
        animate={{
          scale: 1,
          opacity: isDead ? 0.3 : 1,
          filter: isDead ? "grayscale(100%)" : "none",
          boxShadow:
            agent.isExecuting && !isEgg
              ? [
                  "0 0 8px rgba(0,0,0,0)",
                  "0 0 0 1px #00ff8866, 0 0 14px #00ff8840",
                  "0 0 8px rgba(0,0,0,0)",
                ]
              : `0 0 8px ${glowColor}`,
        }}
        exit={
          agent.justDied
            ? {
                opacity: 0,
                scale: 0.85,
                filter: "blur(4px) brightness(0.3)",
                transition: { duration: 1.2 },
              }
            : { opacity: 0 }
        }
        transition={{
          scale: { duration: 0.6, ease: "easeOut" },
          opacity: { duration: isDead ? 2 : 0.6, ease: "easeOut" },
          filter: { duration: isDead ? 2 : 0.6 },
          boxShadow:
            agent.isExecuting && !isEgg
              ? {
                  duration: 1,
                  repeat: Number.POSITIVE_INFINITY,
                  ease: "easeInOut",
                }
              : { duration: 0.4 },
        }}
        className="relative cursor-pointer rounded-sm overflow-hidden"
        style={{
          backgroundColor: "#141414",
          border: isFlashing ? "1px solid #ef4444" : `1px solid ${borderColor}`,
        }}
        onClick={() =>
          navigate({ to: "/agent/$id", params: { id: String(agent.id) } })
        }
        whileHover={
          !isEgg ? { scale: 1.01, boxShadow: `0 0 14px ${glowColor}` } : {}
        }
        whileTap={!isEgg ? { scale: 0.99 } : {}}
      >
        <div className="p-1.5 flex gap-1.5 items-start">
          {/* Pixel sprite */}
          <div className="flex-shrink-0 relative">
            <PixelSprite
              agentId={agent.id}
              tribe={agent.tribe}
              size={40}
              isDead={isDead}
              isEgg={isEgg}
            />
            {agent.isExecuting && !isEgg && (
              <motion.div
                className="absolute inset-0"
                animate={{ opacity: [0, 0.3, 0] }}
                transition={{ duration: 0.6, repeat: Number.POSITIVE_INFINITY }}
                style={{
                  background: `radial-gradient(circle, ${TRIBE_BORDER[agent.tribe]}80 0%, transparent 70%)`,
                }}
              />
            )}
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0 flex flex-col gap-1">
            {/* Name + modality */}
            <div className="flex items-center justify-between gap-1">
              <span
                className="text-xs font-mono font-bold uppercase tracking-wide truncate"
                style={{
                  color: isDead ? "#6b7280" : "#e7e7e7",
                  textDecoration: isDead ? "line-through" : "none",
                }}
              >
                {agent.name}
              </span>
              <span
                className="text-[9px] font-mono font-bold uppercase px-1 py-0.5 rounded-sm flex-shrink-0"
                style={{
                  color: borderColor,
                  backgroundColor: `${borderColor}20`,
                  border: `1px solid ${borderColor}40`,
                }}
              >
                {MODALITY_LABEL[agent.tribe]}
              </span>
            </div>

            {/* State badge + health */}
            <div className="flex flex-col gap-0.5">
              <StateBadge state={agent.state} />
              {!isEgg && <HealthBar health={agent.health} />}
            </div>

            {/* Last task */}
            {agent.lastTask && !isEgg && (
              <p
                className="text-[10px] font-mono truncate"
                style={{ color: "#555" }}
              >
                ↳ {agent.lastTask}
              </p>
            )}

            {isEgg && (
              <p
                className="text-[10px] font-mono"
                style={{ color: "#8b5cf680" }}
              >
                dormant · awaiting birth
              </p>
            )}
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
