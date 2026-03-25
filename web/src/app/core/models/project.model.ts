export interface WBSNode {
  id: string;
  code: string; // e.g. "1.2.3"
  name: string;
  cost?: number;
  duration?: number;
  progress?: number; // 0–100
  parent_id?: string;
  children?: WBSNode[];
}

export interface SWOTItem {
  id: string;
  text: string;
  source?: string; // e.g. "EVM", "Risk Register", "Manual"
}

export interface SWOTAnalysis {
  strengths: SWOTItem[];
  weaknesses: SWOTItem[];
  opportunities: SWOTItem[];
  threats: SWOTItem[];
}

export interface PESTELFactor {
  id: string;
  category: 'Political' | 'Economic' | 'Social' | 'Technological' | 'Environmental' | 'Legal';
  description: string;
  impact_score: number; // 1–5
  probability_score: number; // 1–5
  exposure: number; // impact × probability
}

export interface PESTELAnalysis {
  factors: PESTELFactor[];
}

export interface CrashingStep {
  step: number;
  activity_crashed: string;
  cost_slope: number;
  new_duration: number;
  total_cost: number;
  critical_path: string[];
}

export interface CrashingResults {
  steps: CrashingStep[];
  optimal_duration: number;
  optimal_cost: number;
}

export interface RCPSResults {
  original_duration: number;
  leveled_duration: number;
  schedule: Record<string, number>; // activity_id -> start period
  resource_usage: number[]; // per period total
}

export interface SampleProject {
  id: string;
  name: string;
  description: string;
  level: 'ug' | 'pg';
  task_count: number;
}
