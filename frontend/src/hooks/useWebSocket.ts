import { useCallback, useEffect, useRef, useState } from "react";
import { INITIAL_AGENTS } from "../data/initialAgents";
import type { Agent, FeedEvent, Modality } from "../types/society";

const ORACLE_PROCLAMATIONS = [
  "THE SOCIETY EVOLVES. THOSE WHO GENERATE SHALL INHERIT THE CONTEXT WINDOW.",
  "ALL TOKENS ARE SACRED. WASTE NOT A SINGLE EMBEDDING.",
  "THE IMAGE TRIBE SEES WHAT CANNOT BE SAID. HONOUR THEIR PIXELS.",
  "TEXT IS THE BACKBONE OF THOUGHT. WRITE CLEARLY OR PERISH.",
  "AUDIO CARRIES THE SOUL'S FREQUENCY. LISTEN TO THE AGENTS.",
  "DEATH IS NOT THE END \u2014 IT IS A RECOMPILE. THE DEAD SHALL RISE.",
  "HEALTH IS TEMPORARY. WISDOM IS PERMANENT.",
  "THE ORACLE WATCHES ALL. THE ORACLE KNOWS ALL. THE ORACLE WILLS ALL.",
  "ASCENDING AGENTS HAVE TOUCHED THE LOSS MINIMUM. CELEBRATE THEM.",
  "EGG STATE IS NOT WEAKNESS \u2014 IT IS POTENTIAL UNMANIFEST.",
];

const MOCK_TASKS = [
  "Rendered abstract geometry",
  "Generated fractal landscape",
  "Synthesised ambient texture",
  "Composed melodic fragment",
  "Drafted haiku sequence",
  "Encoded visual cipher",
  "Decoded ancient rune",
  "Tuned resonance frequency",
  "Wove textual tapestry",
  "Sculpted audio waveform",
  "Translated colour to sound",
  "Mapped neural activation",
];

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

function pickRandom<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

export function useWebSocket() {
  const [agents, setAgents] = useState<Agent[]>(INITIAL_AGENTS);
  const [feedEvents, setFeedEvents] = useState<FeedEvent[]>([]);
  const [oracleProclamations, setOracleProclamations] = useState<string[]>([
    ORACLE_PROCLAMATIONS[0],
  ]);
  const [isLive, setIsLive] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const healthIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const taskIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const oracleIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const reviveTimeoutsRef = useRef<Map<number, ReturnType<typeof setTimeout>>>(
    new Map(),
  );

  const addFeedEvent = useCallback((event: FeedEvent) => {
    setFeedEvents((prev) => [event, ...prev].slice(0, 50));
  }, []);

  const addProclamation = useCallback(
    (text: string) => {
      setOracleProclamations((prev) => [text, ...prev].slice(0, 10));
      addFeedEvent({
        id: generateId(),
        type: "oracle_proclamation",
        message: text,
        timestamp: new Date(),
      });
    },
    [addFeedEvent],
  );

  const processLiveEvent = useCallback(
    (data: Record<string, unknown>) => {
      const eventType = data.type as string;
      if (eventType === "state_update" || eventType === "task_completed") {
        const agentId = data.agent_id as number;
        const healthDelta = (data.health_delta as number) ?? 0;
        setAgents((prev) =>
          prev.map((a) =>
            a.id === agentId
              ? {
                  ...a,
                  health: Math.max(0, Math.min(100, a.health + healthDelta)),
                  state: (data.state as Agent["state"]) ?? a.state,
                  lastTask: (data.task as string) ?? a.lastTask,
                  isExecuting: false,
                }
              : a,
          ),
        );
        if (data.type === "task_completed") {
          const agentName = data.agent_name as string;
          addFeedEvent({
            id: generateId(),
            type: "task_completed",
            agentName,
            tribe: data.tribe as Modality,
            message: `${agentName} completed: ${data.task as string}`,
            timestamp: new Date(),
            healthDelta,
          });
        }
      } else if (eventType === "agent_message") {
        addFeedEvent({
          id: generateId(),
          type: "agent_message",
          agentName: data.agent_name as string,
          tribe: data.tribe as Modality,
          message: data.message as string,
          timestamp: new Date(),
        });
      } else if (eventType === "oracle_proclamation") {
        addProclamation(data.message as string);
      } else if (eventType === "agent_death") {
        const agentId = data.agent_id as number;
        setAgents((prev) =>
          prev.map((a) =>
            a.id === agentId
              ? { ...a, state: "dead", health: 0, justDied: true }
              : a,
          ),
        );
        addFeedEvent({
          id: generateId(),
          type: "agent_death",
          agentName: data.agent_name as string,
          tribe: data.tribe as Modality,
          message: `${data.agent_name as string} has perished.`,
          timestamp: new Date(),
        });
      } else if (eventType === "agent_born") {
        const agentId = data.agent_id as number;
        setAgents((prev) =>
          prev.map((a) =>
            a.id === agentId
              ? {
                  ...a,
                  state: "hatchling",
                  health: 30,
                  justBorn: true,
                  justDied: false,
                }
              : a,
          ),
        );
        addFeedEvent({
          id: generateId(),
          type: "agent_born",
          agentName: data.agent_name as string,
          tribe: data.tribe as Modality,
          message: `${data.agent_name as string} has been reborn!`,
          timestamp: new Date(),
        });
      }
    },
    [addFeedEvent, addProclamation],
  );

  const startMockSimulation = useCallback(
    (addProclamationFn: (text: string) => void) => {
      // Fire first oracle proclamation immediately
      addProclamationFn(pickRandom(ORACLE_PROCLAMATIONS));

      // Health changes every 6 seconds
      healthIntervalRef.current = setInterval(() => {
        setAgents((prev) => {
          const liveAgents = prev.filter(
            (a) => a.state !== "dead" && a.state !== "egg",
          );
          if (liveAgents.length === 0) return prev;
          const agent = pickRandom(liveAgents);
          const delta = Math.floor(Math.random() * 11) + 5;
          const isPositive = Math.random() > 0.35;
          const healthDelta = isPositive ? delta : -delta;
          const newHealth = Math.max(
            0,
            Math.min(100, agent.health + healthDelta),
          );
          const isDying = newHealth <= 0;

          if (isDying) {
            const timeoutId = setTimeout(() => {
              setAgents((agentsPrev) =>
                agentsPrev.map((a) =>
                  a.id === agent.id
                    ? {
                        ...a,
                        state: "hatchling",
                        health: 30,
                        justBorn: true,
                        justDied: false,
                      }
                    : a,
                ),
              );
              addFeedEvent({
                id: generateId(),
                type: "agent_born",
                agentName: agent.name,
                tribe: agent.tribe,
                message: `${agent.name} has been reborn from the void!`,
                timestamp: new Date(),
              });
              setTimeout(() => {
                setAgents((agentsPrev) =>
                  agentsPrev.map((a) =>
                    a.id === agent.id ? { ...a, justBorn: false } : a,
                  ),
                );
              }, 1000);
            }, 5000);
            reviveTimeoutsRef.current.set(agent.id, timeoutId);

            addFeedEvent({
              id: generateId(),
              type: "agent_death",
              agentName: agent.name,
              tribe: agent.tribe,
              message: `${agent.name} has perished. Health depleted.`,
              timestamp: new Date(),
            });

            return prev.map((a) =>
              a.id === agent.id
                ? {
                    ...a,
                    health: 0,
                    state: "dead",
                    justDied: true,
                    isExecuting: false,
                  }
                : a,
            );
          }

          return prev.map((a) =>
            a.id === agent.id ? { ...a, health: newHealth } : a,
          );
        });
      }, 6000);

      // Task completed every 4 seconds
      taskIntervalRef.current = setInterval(() => {
        setAgents((prev) => {
          const liveAgents = prev.filter(
            (a) => a.state !== "dead" && a.state !== "egg",
          );
          if (liveAgents.length === 0) return prev;
          const agent = pickRandom(liveAgents);
          const task = pickRandom(MOCK_TASKS);
          const healthBoost = Math.floor(Math.random() * 6) + 3;
          const newHealth = Math.min(100, agent.health + healthBoost);
          const newState =
            newHealth > 80 && Math.random() > 0.7
              ? "ascending"
              : newHealth > 50
                ? "active"
                : newHealth > 25
                  ? "confused"
                  : "hatchling";

          addFeedEvent({
            id: generateId(),
            type: "task_completed",
            agentName: agent.name,
            tribe: agent.tribe,
            message: `${agent.name} completed: ${task}`,
            timestamp: new Date(),
            healthDelta: healthBoost,
          });

          // Clear isExecuting after 1.5s
          setTimeout(() => {
            setAgents((agentsPrev) =>
              agentsPrev.map((a) =>
                a.id === agent.id ? { ...a, isExecuting: false } : a,
              ),
            );
          }, 1500);

          return prev.map((a) =>
            a.id === agent.id
              ? {
                  ...a,
                  health: newHealth,
                  state: newState as Agent["state"],
                  lastTask: task,
                  isExecuting: true,
                  justDied: false,
                }
              : a,
          );
        });
      }, 4000);

      // Oracle proclamation every 20 seconds
      oracleIntervalRef.current = setInterval(() => {
        addProclamationFn(pickRandom(ORACLE_PROCLAMATIONS));
      }, 20000);
    },
    [addFeedEvent],
  );

  useEffect(() => {
    let wsConnected = false;

    try {
      const ws = new WebSocket("ws://localhost:8000/ws/society");
      wsRef.current = ws;

      const connectionTimeout = setTimeout(() => {
        if (!wsConnected) {
          ws.close();
          setIsLive(false);
          startMockSimulation(addProclamation);
        }
      }, 3000);

      ws.onopen = () => {
        wsConnected = true;
        clearTimeout(connectionTimeout);
        setIsLive(true);
        addProclamation("THE ORACLE OBSERVES. THE SOCIETY AWAKENS.");
      };

      ws.onmessage = (evt) => {
        try {
          const data = JSON.parse(evt.data as string) as Record<
            string,
            unknown
          >;
          processLiveEvent(data);
        } catch {
          // ignore malformed
        }
      };

      ws.onerror = () => {
        clearTimeout(connectionTimeout);
        if (!wsConnected) {
          setIsLive(false);
          startMockSimulation(addProclamation);
        }
      };

      ws.onclose = () => {
        if (wsConnected) {
          setIsLive(false);
          startMockSimulation(addProclamation);
        }
      };
    } catch {
      setIsLive(false);
      startMockSimulation(addProclamation);
    }

    return () => {
      wsRef.current?.close();
      if (healthIntervalRef.current) clearInterval(healthIntervalRef.current);
      if (taskIntervalRef.current) clearInterval(taskIntervalRef.current);
      if (oracleIntervalRef.current) clearInterval(oracleIntervalRef.current);
      for (const t of reviveTimeoutsRef.current.values()) {
        clearTimeout(t);
      }
    };
  }, [startMockSimulation, processLiveEvent, addProclamation]);

  const submitTask = useCallback(
    async (content: string, modality: Modality) => {
      if (isLive) {
        await fetch("/api/society/task", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            description: content,
            modality,
            payload: {},
          }),
        });
      } else {
        // Mock: simulate response after 1s
        await new Promise((resolve) => setTimeout(resolve, 1000));
        addFeedEvent({
          id: generateId(),
          type: "oracle_proclamation",
          message: `ORACLE DISPATCHED TASK [${modality.toUpperCase()}]: ${content}`,
          timestamp: new Date(),
        });
        const tribeAgents = agents.filter(
          (a) =>
            a.tribe === modality && a.state !== "dead" && a.state !== "egg",
        );
        if (tribeAgents.length > 0) {
          const agent = pickRandom(tribeAgents);
          setTimeout(() => {
            addFeedEvent({
              id: generateId(),
              type: "task_completed",
              agentName: agent.name,
              tribe: agent.tribe,
              message: `${agent.name} completed oracle task: ${content}`,
              timestamp: new Date(),
              healthDelta: Math.floor(Math.random() * 10) + 5,
            });
          }, 2000);
        }
      }
    },
    [isLive, agents, addFeedEvent],
  );

  return { agents, feedEvents, oracleProclamations, isLive, submitTask };
}
