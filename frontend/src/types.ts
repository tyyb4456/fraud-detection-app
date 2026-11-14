export type FormValues = Record<string, string | number | boolean>;
export type Categories = Record<string, string[]>;

export interface Reason {
  feature: string;
  value: string | number | boolean;
  impact: number; // log-odds contribution; positive pushes toward fraud
}

export interface Prediction {
  fraud_probability: number;
  flagged: boolean;
  threshold: number;
  top_reasons: Reason[];
}