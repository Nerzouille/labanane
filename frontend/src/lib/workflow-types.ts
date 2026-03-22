import { z } from 'zod';

// ── Product type ────────────────────────────────────────────────────────────
export const ProductSchema = z.object({
  title: z.string(),
  price: z.string(),
  url: z.string(),
  rating_stars: z.number(),
  rating_range: z.number(),
  rating_count: z.number(),
  main_features: z.array(z.string()),
  image_url: z.string().optional(),
});
export type Product = z.infer<typeof ProductSchema>;

// ── Step data schemas (component_type → data shape) ─────────────────────────

export const KeywordListDataSchema = z.object({
  keywords: z.array(z.string()),
});

export const ProductListDataSchema = z.object({
  products: z.array(ProductSchema),
  source_keywords: z.array(z.string()),
});

export const TimePointSchema = z.object({ date: z.string(), value: z.number() });
export const RegionPointSchema = z.object({ geo: z.string(), name: z.string(), value: z.number() });
export const QueryPointSchema = z.object({ query: z.string(), value: z.number() });
export const RisingPointSchema = z.object({ query: z.string(), value: z.string() });

export const KeywordTrendsSchema = z.object({
  interest_over_time: z.array(TimePointSchema),
  interest_by_region: z.array(RegionPointSchema),
  related_queries_top: z.array(QueryPointSchema),
  related_queries_rising: z.array(RisingPointSchema),
});

export const MarketDataResultSchema = z.object({
  keywords: z.array(z.string()),
  sources_available: z.array(z.string()),
  sources_unavailable: z.array(z.string()),
  trends: z.record(KeywordTrendsSchema),
});

export const CriterionSchema = z.object({ label: z.string(), score: z.number() });

export const AiAnalysisDataSchema = z.object({
  viability_score: z.number(),
  go_no_go: z.enum(['go', 'no-go', 'conditional']),
  summary: z.string(),
  analysis: z.string(),
  key_risks: z.array(z.string()),
  key_opportunities: z.array(z.string()),
  criteria: z.array(CriterionSchema),
  target_persona: z.object({ description: z.string() }),
  differentiation_angles: z.object({ content: z.string() }),
  competitive_overview: z.object({ content: z.string() }),
});

export const PersonaSchema = z.object({
  name: z.string(),
  age_range: z.string(),
  occupation: z.string(),
  motivations: z.array(z.string()),
  pain_points: z.array(z.string()),
});

export const PersonaSetDataSchema = z.object({
  personas: z.array(PersonaSchema),
});

export type Persona = z.infer<typeof PersonaSchema>;
export type PersonaSetData = z.infer<typeof PersonaSetDataSchema>;

export const FinalCriteriaDataSchema = z.object({
  summary: z.string(),
  go_no_go: z.enum(['go', 'no-go', 'conditional']),
  key_risks: z.array(z.string()),
  key_opportunities: z.array(z.string()),
});

export const ReportDataSchema = z.object({
  run_id: z.string(),
  markdown_available: z.boolean(),
});

export type KeywordListData = z.infer<typeof KeywordListDataSchema>;
export type ProductListData = z.infer<typeof ProductListDataSchema>;
export type TimePoint = z.infer<typeof TimePointSchema>;
export type RegionPoint = z.infer<typeof RegionPointSchema>;
export type QueryPoint = z.infer<typeof QueryPointSchema>;
export type RisingPoint = z.infer<typeof RisingPointSchema>;
export type KeywordTrends = z.infer<typeof KeywordTrendsSchema>;
export type MarketDataResult = z.infer<typeof MarketDataResultSchema>;
export type Criterion = z.infer<typeof CriterionSchema>;
export type AiAnalysisData = z.infer<typeof AiAnalysisDataSchema>;
export type FinalCriteriaData = z.infer<typeof FinalCriteriaDataSchema>;
export type ReportData = z.infer<typeof ReportDataSchema>;

// ── Server → Client message schemas ────────────────────────────────────────

export const WorkflowStartedSchema = z.object({
  type: z.literal('workflow_started'),
  total_steps: z.number(),
  step_ids: z.array(z.string()),
});

export const StepActivatedSchema = z.object({
  type: z.literal('step_activated'),
  step_id: z.string(),
  step_number: z.number(),
  total_steps: z.number(),
  label: z.string(),
});

export const StepProcessingSchema = z.object({
  type: z.literal('step_processing'),
  step_id: z.string(),
});

export const StepResultSchema = z.object({
  type: z.literal('step_result'),
  step_id: z.string(),
  component_type: z.string(),
  data: z.record(z.string(), z.unknown()),
});

export const ConfirmationRequestSchema = z.object({
  type: z.literal('confirmation_request'),
  step_id: z.string(),
  component_type: z.string(),
  data: z.record(z.string(), z.unknown()),
});

export const StepErrorSchema = z.object({
  type: z.literal('step_error'),
  step_id: z.string(),
  error: z.string(),
  retryable: z.boolean(),
});

export const WorkflowCompleteSchema = z.object({
  type: z.literal('workflow_complete'),
  run_id: z.string(),
});

export const ServerMessageSchema = z.discriminatedUnion('type', [
  WorkflowStartedSchema,
  StepActivatedSchema,
  StepProcessingSchema,
  StepResultSchema,
  ConfirmationRequestSchema,
  StepErrorSchema,
  WorkflowCompleteSchema,
]);

export type WorkflowStarted = z.infer<typeof WorkflowStartedSchema>;
export type StepActivated = z.infer<typeof StepActivatedSchema>;
export type StepProcessing = z.infer<typeof StepProcessingSchema>;
export type StepResult = z.infer<typeof StepResultSchema>;
export type ConfirmationRequest = z.infer<typeof ConfirmationRequestSchema>;
export type StepError = z.infer<typeof StepErrorSchema>;
export type WorkflowComplete = z.infer<typeof WorkflowCompleteSchema>;
export type ServerMessage = z.infer<typeof ServerMessageSchema>;

// ── Workflow state types ────────────────────────────────────────────────────

export type WsStatus = 'idle' | 'connecting' | 'open' | 'closed' | 'error';
export type StepStatus = 'pending' | 'active' | 'processing' | 'result' | 'confirmation' | 'error' | 'complete';

export interface StepState {
  step_id: string;
  step_number: number;
  label: string;
  status: StepStatus;
  component_type?: string;
  data?: Record<string, unknown>;
  error?: string;
}
