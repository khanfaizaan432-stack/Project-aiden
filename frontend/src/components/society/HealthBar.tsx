interface HealthBarProps {
  health: number;
  showValue?: boolean;
}

export function HealthBar({ health, showValue = true }: HealthBarProps) {
  const clampedHealth = Math.max(0, Math.min(100, health));

  let barColor: string;
  let glowColor: string;
  if (clampedHealth > 60) {
    barColor = "#00ff88";
    glowColor = "rgba(0,255,136,0.4)";
  } else if (clampedHealth > 30) {
    barColor = "#f59e0b";
    glowColor = "rgba(245,158,11,0.4)";
  } else {
    barColor = "#ef4444";
    glowColor = "rgba(239,68,68,0.4)";
  }

  return (
    <div className="flex items-center gap-2 w-full">
      <div
        className="w-full rounded-full overflow-hidden"
        style={{ backgroundColor: "#2a2a2a", height: "4px" }}
      >
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{
            width: `${clampedHealth}%`,
            backgroundColor: barColor,
            boxShadow: clampedHealth > 0 ? `0 0 4px ${glowColor}` : "none",
          }}
        />
      </div>
      {showValue && (
        <span
          className="text-xs font-mono tabular-nums w-7 text-right"
          style={{ color: barColor }}
        >
          {clampedHealth}
        </span>
      )}
    </div>
  );
}
