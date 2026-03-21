import { z } from 'zod';

// ── Product type ────────────────────────────────────────────────────────────
export const ProductSchema = z.object({
  title: z.string(),
  price: z.string(),
  url: z.string(),
});
export type Product = z.infer<typeof ProductSchema>;

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

export const StepStreamingTokenSchema = z.object({
  type: z.literal('step_streaming_token'),
  step_id: z.string(),
  token: z.string(),
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
  StepStreamingTokenSchema,
  StepResultSchema,
  ConfirmationRequestSchema,
  StepErrorSchema,
  WorkflowCompleteSchema,
]);

export type WorkflowStarted = z.infer<typeof WorkflowStartedSchema>;
export type StepActivated = z.infer<typeof StepActivatedSchema>;
export type StepProcessing = z.infer<typeof StepProcessingSchema>;
export type StepStreamingToken = z.infer<typeof StepStreamingTokenSchema>;
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
  tokens?: string; // accumulated streaming tokens
}
