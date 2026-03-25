export interface EVMTask {
  task_id: string;
  name: string;
  budget: number;
  pct_complete: number;
  planned_start: number;
  planned_finish: number;
}

export interface EVMPeriod {
  index: number;
  label: string;
  pv_cumulative: number;
  ev_cumulative: number;
  ac_cumulative: number;
}

export interface EVMProject {
  project_name: string;
  bac: number;
  currency_symbol: string;
  periods: EVMPeriod[];
  tasks: EVMTask[];
}

export interface EVMKPIs {
  ev: number;
  cv: number;
  sv: number;
  cpi: number;
  spi: number;
  pc: number;
  ps: number;
  cr: number;
  eac1: number;
  eac2: number;
  eac3: number;
  vac: number;
  tcpi_bac: number;
}

export type RAGStatus = 'red' | 'amber' | 'green';
