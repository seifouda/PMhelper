export interface MCResults {
  durations: number[];
  costs: number[];
  cp_frequencies: Record<string, number>;
  p50_duration: number;
  p80_duration: number;
  p90_duration: number;
  p_cost_within_bac: number;
  n_trials: number;
}
