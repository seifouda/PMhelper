export interface Activity {
  id: string;
  activity: string;
  duration: number;
  predecessors: string[];
  min_duration?: number;
  crash_cost?: number;
  resource_demand?: number;
  normal_cost?: number;
  optimistic?: number;
  most_likely?: number;
  pessimistic?: number;
}
