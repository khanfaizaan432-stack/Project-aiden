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
  | "agent_born"
  | "evaluation_result";

export interface FeedEvent {
  id: string;
  type: EventType;
  agentName?: string;
  tribe?: Modality;
  message: string;
  timestamp: Date;
  healthDelta?: number;
  predictedClass?: string;
  probabilities?: Record<string, number>;
  agentNames?: string[];
}

export interface EvaluateVote {
  agent_id: number;
  agent_name: string;
  probabilities: Record<string, number>;
}

export interface EvaluateResponse {
  agent_id: number;
  agent_name: string;
  agent_ids: number[];
  agent_names: string[];
  predicted: string;
  probabilities: Record<string, number>;
  votes: EvaluateVote[];
}
