export interface CPMNode {
  id: string;
  activity: string;
  duration: number;
  ES: number;
  EF: number;
  LS: number;
  LF: number;
  total_float: number;
  free_float: number;
  is_critical: boolean;
}

export interface CPMEdge {
  from: string;
  to: string;
}

export interface CPMResults {
  project_duration: number;
  critical_paths: string[][];
  critical_activities: string[];
  nodes: CPMNode[];
  edges: CPMEdge[];
}
