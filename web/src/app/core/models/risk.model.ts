export type RiskCategory = 'Schedule' | 'Cost' | 'Quality' | 'Scope' | 'Other';

export interface Risk {
  id: string;
  name: string;
  description: string;
  probability: number; // 0–1 or 1–5 scale
  impact: number; // monetary impact or 1–5 scale
  category: RiskCategory;
  exposure: number; // computed: probability × impact
}

export interface RiskResults {
  risks: Risk[];
  total_exposure: number;
  contingency_reserve: number;
}
