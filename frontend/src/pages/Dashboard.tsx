import { OracleBanner } from "../components/society/OracleBanner";
import { OraclePanel } from "../components/society/OraclePanel";
import { SocietyFeed } from "../components/society/SocietyFeed";
import { TribeColumn } from "../components/society/TribeColumn";
import { useWebSocket } from "../hooks/useWebSocket";

export function Dashboard() {
  const { agents, feedEvents, oracleProclamations, isLive, submitTask } =
    useWebSocket();
  const latestProclamation =
    oracleProclamations[0] ?? "AWAITING ORACLE SIGNAL...";

  return (
    <div
      className="min-h-screen font-mono"
      style={{
        backgroundColor: "#0a0a0a",
        backgroundImage:
          "radial-gradient(ellipse at center, #0a0a0a 55%, #050505 100%)",
      }}
    >
      {/* Top bar */}
      <header className="px-7 pt-6 pb-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1
            className="text-3xl font-mono font-black uppercase tracking-[0.15em]"
            style={{ color: "#f59e0b" }}
          >
            AI SOCIETY
          </h1>
          <span
            className="text-[10px] font-mono uppercase tracking-wider px-1.5 py-0.5 rounded-sm hidden sm:block"
            style={{ color: "#555", border: "1px solid #222" }}
          >
            v0.1.0-alpha
          </span>
        </div>

        {/* Connection status pill */}
        <div
          data-ocid="status.pill"
          className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-mono font-bold uppercase tracking-wide"
          style={{
            backgroundColor: isLive
              ? "rgba(31,122,58,0.3)"
              : "rgba(127,29,29,0.3)",
            border: `1px solid ${isLive ? "#2a8a47" : "#7f1d1d"}`,
            color: isLive ? "#66f0a3" : "#ef4444",
          }}
        >
          <span
            className="w-1.5 h-1.5 rounded-full"
            style={{
              backgroundColor: isLive ? "#66f0a3" : "#ef4444",
              boxShadow: isLive ? "0 0 4px #66f0a3" : "0 0 4px #ef4444",
            }}
          />
          {isLive ? "LIVE" : "MOCK"}
        </div>
      </header>

      {/* Oracle proclamation banner */}
      <div className="px-7 mb-3">
        <OracleBanner proclamation={latestProclamation} />
      </div>

      {/* Main content: tribe columns + feed sidebar */}
      <div className="px-7 flex gap-4">
        {/* Three tribe columns */}
        <div className="flex-1 grid grid-cols-3 gap-4 min-w-0">
          <TribeColumn tribe="image" agents={agents} />
          <TribeColumn tribe="text" agents={agents} />
          <TribeColumn tribe="audio" agents={agents} />
        </div>

        {/* Society Event Feed sidebar */}
        <div className="flex-shrink-0" style={{ width: 300 }}>
          <SocietyFeed events={feedEvents} />
        </div>
      </div>

      {/* Oracle Panel */}
      <div className="px-7 mt-4 pb-6">
        <OraclePanel
          oracleProclamations={oracleProclamations}
          onSubmitTask={submitTask}
        />
      </div>

      {/* Footer */}
      <footer className="px-7 pb-4 flex justify-center">
        <a
          href={`https://caffeine.ai?utm_source=caffeine-footer&utm_medium=referral&utm_content=${encodeURIComponent(typeof window !== "undefined" ? window.location.hostname : "")}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-[10px] font-mono uppercase tracking-wider transition-colors"
          style={{ color: "#333" }}
          onMouseEnter={(e) => {
            e.currentTarget.style.color = "#555";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = "#333";
          }}
        >
          © {new Date().getFullYear()} · Built with ♥ using caffeine.ai
        </a>
      </footer>
    </div>
  );
}
