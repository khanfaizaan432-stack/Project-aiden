import { useNavigate, useParams } from "@tanstack/react-router";

export function AgentDetail() {
  const navigate = useNavigate();
  const params = useParams({ strict: false }) as { id?: string };
  const id = params.id;

  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center font-mono"
      style={{ backgroundColor: "#0a0a0a" }}
    >
      <div
        className="p-8 rounded-sm text-center"
        style={{ border: "1px solid #2a2a2a", backgroundColor: "#101010" }}
      >
        <div className="text-4xl mb-4">⬡</div>
        <h1
          className="text-2xl font-black uppercase tracking-widest mb-2"
          style={{ color: "#f59e0b" }}
        >
          AGENT DETAIL
        </h1>
        <p
          className="text-sm uppercase tracking-wider mb-6"
          style={{ color: "#555" }}
        >
          {"COMING SOON \u00b7 ID: "}
          {id}
        </p>
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
      </div>
    </div>
  );
}
