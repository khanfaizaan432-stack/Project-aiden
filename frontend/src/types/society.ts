export type AgentState =
  | "egg"
  | "hatchling"
  | "active"
  | "ascending"
  | "confused"
  | "dead";
export type Modality = "image" | "text" | "audio";

export interface Agent {
  id: number;
  name: string;
  tribe: Modality;
  state: AgentState;
  health: number;
  personality: string;
  lastTask?: string;
  isExecuting?: boolean;
  justDied?: boolean;
  justBorn?: boolean;
}

export type EventType =
  | "task_completed"
  | "agent_message"
  | "oracle_proclamation"
  | "agent_death"
  | "agent_born";

export interface FeedEvent {
  id: string;
  type: EventType;
  agentName?: string;
  tribe?: Modality;
  message: string;
  timestamp: Date;
  healthDelta?: number;
}
