import { AnimatePresence, motion } from "motion/react";
import { useState } from "react";
import type { Modality } from "../../types/society";

interface OraclePanelProps {
  oracleProclamations: string[];
  onSubmitTask: (content: string, modality: Modality) => Promise<void>;
  onEvaluateImage: (imageFile: File) => Promise<void>;
}

export function OraclePanel({
  oracleProclamations,
  onSubmitTask,
  onEvaluateImage,
}: OraclePanelProps) {
  const [input, setInput] = useState("");
  const [modality, setModality] = useState<Modality>("image");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (isSubmitting) return;

    const shouldEvaluateImage = modality === "image";
    if (shouldEvaluateImage && !imageFile) {
      setError("Select an image before evaluating.");
      return;
    }

    if (!shouldEvaluateImage && !input.trim()) return;

    setIsSubmitting(true);
    setError(null);
    try {
      if (shouldEvaluateImage && imageFile) {
        await onEvaluateImage(imageFile);
        setImageFile(null);
      } else {
        await onSubmitTask(input.trim(), modality);
        setInput("");
      }
      setSubmitted(true);
      setTimeout(() => setSubmitted(false), 2500);
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : "Failed to dispatch request.",
      );
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

  const handleModalityChange = (nextModality: Modality) => {
    setModality(nextModality);
    setError(null);
    if (nextModality !== "image") {
      setImageFile(null);
    }
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
        {/* Left: Task input or image upload */}
        <div className="flex-1 flex flex-col gap-2">
          <span
            className="text-[10px] font-mono font-bold uppercase tracking-widest"
            style={{ color: "#f59e0b88" }}
          >
            {modality === "image" ? "IMAGE UPLOAD" : "ORACLE TASK INPUT"}
          </span>
          {modality === "image" ? (
            <label
              className="flex items-center justify-between gap-3 px-3 py-2 text-sm font-mono rounded-sm transition-all cursor-pointer"
              style={{
                backgroundColor: "#0e0e0e",
                border: "1px dashed #2a2a2a",
                color: imageFile ? "#e7e7e7" : "#666",
              }}
            >
              <input
                id="oracle-image-input"
                data-ocid="oracle.image.input"
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => {
                  setImageFile(e.target.files?.[0] ?? null);
                  setError(null);
                }}
              />
              <span className="truncate">
                {imageFile ? imageFile.name : "Choose an image to evaluate..."}
              </span>
              <span className="text-[10px] font-bold uppercase tracking-widest text-[#f59e0b88]">
                Browse
              </span>
            </label>
          ) : (
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
          )}
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
                    onClick={() => handleModalityChange(m)}
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
              disabled={
                isSubmitting || (modality === "image" ? !imageFile : !input.trim())
              }
              className="px-4 py-1.5 rounded-sm text-xs font-mono font-bold uppercase tracking-widest transition-all ml-2"
              style={{
                backgroundColor:
                  isSubmitting || (modality === "image" ? !imageFile : !input.trim())
                    ? "#1a1a1a"
                    : "rgba(245,158,11,0.15)",
                border: `1px solid ${isSubmitting || (modality === "image" ? !imageFile : !input.trim()) ? "#2a2a2a" : "#c98b36"}`,
                color:
                  isSubmitting || (modality === "image" ? !imageFile : !input.trim())
                    ? "#444"
                    : "#f59e0b",
                cursor:
                  isSubmitting || (modality === "image" ? !imageFile : !input.trim())
                    ? "not-allowed"
                    : "pointer",
              }}
              whileHover={
                !isSubmitting && (modality === "image" ? Boolean(imageFile) : Boolean(input.trim()))
                  ? { scale: 1.02, boxShadow: "0 0 10px rgba(245,158,11,0.3)" }
                  : {}
              }
              whileTap={
                !isSubmitting && (modality === "image" ? Boolean(imageFile) : Boolean(input.trim()))
                  ? { scale: 0.98 }
                  : {}
              }
            >
              {isSubmitting
                ? "DISPATCHING..."
                : modality === "image"
                  ? "EVALUATE IMAGE"
                  : "INITIATE TASK"}
            </motion.button>
          </div>

          {error && (
            <div
              className="text-[10px] font-mono uppercase tracking-widest"
              style={{ color: "#ef4444" }}
            >
              {error}
            </div>
          )}

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
                {modality === "image"
                  ? "✓ IMAGE EVALUATED BY ENSEMBLE"
                  : "✓ TASK DISPATCHED TO SOCIETY"}
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
