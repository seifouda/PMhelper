export interface PERTNode {
  id: string;
  activity: string;
  optimistic: number;
  most_likely: number;
  pessimistic: number;
  expected_time: number;
  variance: number;
  std_dev: number;
}

export interface PERTResults {
  nodes: PERTNode[];
  project_expected_duration: number;
  project_variance: number;
  project_std_dev: number;
  /** P(T <= target_duration) */
  probability_on_time?: number;
}
