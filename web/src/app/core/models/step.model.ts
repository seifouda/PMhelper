export interface CalculationStep {
  title: string;
  formula: string; // KaTeX source
  substitution: string; // KaTeX with actual values substituted
  result: string; // KaTeX result expression
  explanation: string; // Plain English description
  highlight_nodes?: string[];
}
