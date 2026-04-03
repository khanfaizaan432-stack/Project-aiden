import { AnimatePresence, motion } from "motion/react";
import { useState } from "react";
import type { Modality } from "../../types/society";

interface OraclePanelProps {
  oracleProclamations: string[];
  onSubmitTask: (content: string, modality: Modality) => Promise<void>;
}

export function OraclePanel({
  oracleProclamations,
  onSubmitTask,
}: OraclePanelProps) {
  const [input, setInput] = useState("");
  const [modality, setModality] = useState<Modality>("image");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async () => {
    if (!input.trim() || isSubmitting) return;
    setIsSubmitting(true);
    try {
      await onSubmitTask(input.trim(), modality);
      setSubmitted(true);
      setInput("");
      setTimeout(() => setSubmitted(false), 2500);
    } finally {
      setIsSubmitting(false);
    }
  };

  const MODALITY_CONFIG: Record<
    Modality,
    { label: string; icon: string; color: string; border: string }
  > = {
    image: { label: "IMAGE", icon: "🖼", color: "#2ea36a", border: "#2a6642" },
    text: { label: "TEXT", icon: "📝", color: "#c08a3a", border: "#6b4c1e" },
    audio: { label: "AUDIO", icon: "🔊", color: "#3b82b8", border: "#1e4a6e" },
  };

  return (
    <div
      className="w-full rounded-sm p-4"
      style={{
        border: "1px solid #c98b3644",
        backgroundColor: "rgba(201,139,54,0.04)",
      }}
    >
      <div className="flex flex-col lg:flex-row gap-4">
        {/* Left: Task input */}
        <div className="flex-1 flex flex-col gap-2">
          <span
            className="text-[10px] font-mono font-bold uppercase tracking-widest"
            style={{ color: "#f59e0b88" }}
          >
            ORACLE TASK INPUT
          </span>
          <div className="flex gap-2">
            <input
              id="oracle-task-input"
              data-ocid="oracle.input"
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
              placeholder="Enter task for the society..."
              className="flex-1 px-3 py-2 text-sm font-mono rounded-sm outline-none transition-all"
              style={{
                backgroundColor: "#0e0e0e",
                border: "1px solid #2a2a2a",
                color: "#e7e7e7",
                caretColor: "#f59e0b",
              }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = "#c98b36";
                e.currentTarget.style.boxShadow =
                  "0 0 8px rgba(201,139,54,0.2)";
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = "#2a2a2a";
                e.currentTarget.style.boxShadow = "none";
              }}
            />
          </div>
        </div>

        {/* Right: Modality + submit */}
        <div className="flex flex-col gap-2">
          <span
            className="text-[10px] font-mono font-bold uppercase tracking-widest"
            style={{ color: "#f59e0b88" }}
          >
            MODALITY SELECTOR
          </span>
          <div className="flex gap-2 items-center">
            {/* Modality buttons */}
            <div className="flex gap-1">
              {(["image", "text", "audio"] as Modality[]).map((m) => {
                const cfg = MODALITY_CONFIG[m];
                const isSelected = modality === m;
                return (
                  <button
                    key={m}
                    data-ocid={`oracle.${m}.toggle`}
                    type="button"
                    onClick={() => setModality(m)}
                    className="px-2 py-1.5 rounded-sm text-[10px] font-mono font-bold uppercase tracking-wide transition-all"
                    style={{
                      backgroundColor: isSelected
                        ? `${cfg.border}44`
                        : "transparent",
                      border: `1px solid ${isSelected ? cfg.color : "#2a2a2a"}`,
                      color: isSelected ? cfg.color : "#555",
                      boxShadow: isSelected
                        ? `0 0 6px ${cfg.border}40`
                        : "none",
                    }}
                  >
                    {cfg.icon} {cfg.label}
                  </button>
                );
              })}
            </div>

            {/* Submit button */}
            <motion.button
              data-ocid="oracle.submit_button"
              type="button"
              onClick={handleSubmit}
              disabled={isSubmitting || !input.trim()}
              className="px-4 py-1.5 rounded-sm text-xs font-mono font-bold uppercase tracking-widest transition-all ml-2"
              style={{
                backgroundColor:
                  isSubmitting || !input.trim()
                    ? "#1a1a1a"
                    : "rgba(245,158,11,0.15)",
                border: `1px solid ${isSubmitting || !input.trim() ? "#2a2a2a" : "#c98b36"}`,
                color: isSubmitting || !input.trim() ? "#444" : "#f59e0b",
                cursor:
                  isSubmitting || !input.trim() ? "not-allowed" : "pointer",
              }}
              whileHover={
                !isSubmitting && input.trim()
                  ? { scale: 1.02, boxShadow: "0 0 10px rgba(245,158,11,0.3)" }
                  : {}
              }
              whileTap={!isSubmitting && input.trim() ? { scale: 0.98 } : {}}
            >
              {isSubmitting ? "DISPATCHING..." : "INITIATE TASK"}
            </motion.button>
          </div>

          {/* Success flash */}
          <AnimatePresence>
            {submitted && (
              <motion.div
                data-ocid="oracle.success_state"
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="text-[10px] font-mono uppercase tracking-widest"
                style={{ color: "#22c55e" }}
              >
                ✓ TASK DISPATCHED TO SOCIETY
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Last proclamations */}
      {oracleProclamations.length > 0 && (
        <div className="mt-3 pt-3" style={{ borderTop: "1px solid #c98b3622" }}>
          <div
            className="text-[9px] font-mono font-bold uppercase tracking-widest mb-2"
            style={{ color: "#f59e0b44" }}
          >
            LAST PROCLAMATIONS
          </div>
          <div className="flex flex-col gap-1">
            {oracleProclamations.slice(0, 3).map((p, i) => (
              <div
                key={p.slice(0, 20)}
                data-ocid={`oracle.proclamation.item.${i + 1}`}
                className="text-[10px] font-mono uppercase tracking-wide"
                style={{
                  color:
                    i === 0 ? "#f2a23a" : i === 1 ? "#c08a3a80" : "#8a5a2a60",
                }}
              >
                ⚡ {p}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
