interface OracleBannerProps {
  proclamation: string;
}

export function OracleBanner({ proclamation }: OracleBannerProps) {
  return (
    <div
      className="w-full rounded-sm overflow-hidden"
      style={{
        border: "1px solid #c98b36",
        backgroundColor: "rgba(201,139,54,0.06)",
      }}
    >
      <div className="marquee-container py-2 px-4">
        <span
          className="marquee-text text-sm font-mono font-bold uppercase tracking-widest"
          style={{ color: "#f2a23a" }}
        >
          ⚡ [PROCLAMATION]: {proclamation} ✦ ⚡ [PROCLAMATION]: {proclamation}{" "}
          ✦
        </span>
      </div>
    </div>
  );
}
