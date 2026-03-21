import { z } from 'zod';

export const SSEPayloadSchema = z.object({
    id: z.number().int().nonnegative(),
    status: z.enum(['processing', 'done', 'error']),
    percentage: z.number().min(0).max(100),
    message: z.string(),
});

export type SSEPayload = z.infer<typeof SSEPayloadSchema>;

export type ConnectionState = 'idle' | 'connecting' | 'streaming' | 'done' | 'error';
