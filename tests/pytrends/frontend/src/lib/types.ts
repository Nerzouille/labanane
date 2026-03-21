import { z } from 'zod';

// ---------------------------------------------------------------------------
// Connection state
// ---------------------------------------------------------------------------

export type ConnectionState = 'idle' | 'connecting' | 'streaming' | 'done' | 'error';

// ---------------------------------------------------------------------------
// SSE event names
// ---------------------------------------------------------------------------

export type SSEEventName =
    | 'google_trends'
    | 'marketplace_products'
    | 'export_ready'
    | 'source_unavailable';

// ---------------------------------------------------------------------------
// google_trends event
// ---------------------------------------------------------------------------

export const TrendsDataPointSchema = z.object({ date: z.string(), value: z.number().int() });
export const TrendsRegionSchema = z.object({ name: z.string(), value: z.number().int() });
export const GoogleTrendsEventSchema = z.object({
    status: z.literal('complete'),
    keyword: z.string(),
    interest: z.array(TrendsDataPointSchema),
    trend_pct: z.number().int(),
    seasonality: z.string(),
    regions: z.array(TrendsRegionSchema),
    top_market: z.string(),
    opportunity: z.string(),
});

export type TrendsDataPoint = z.infer<typeof TrendsDataPointSchema>;
export type TrendsRegion = z.infer<typeof TrendsRegionSchema>;
export type GoogleTrendsEvent = z.infer<typeof GoogleTrendsEventSchema>;

// ---------------------------------------------------------------------------
// marketplace_products event
// ---------------------------------------------------------------------------

export const MarketplaceProductSchema = z.object({
    title: z.string(),
    price: z.number(),
    currency: z.string().default('USD'),
    rating: z.number().nullable().optional(),
    reviews: z.number().int().nullable().optional(),
    url: z.string().nullable().optional(),
});

export const MarketplaceProductsEventSchema = z.object({
    status: z.literal('complete'),
    source: z.string(),
    keyword: z.string(),
    products: z.array(MarketplaceProductSchema),
});

export type MarketplaceProduct = z.infer<typeof MarketplaceProductSchema>;
export type MarketplaceProductsEvent = z.infer<typeof MarketplaceProductsEventSchema>;

// ---------------------------------------------------------------------------
// export_ready event
// ---------------------------------------------------------------------------

export const ExportReadyEventSchema = z.object({
    status: z.literal('ready'),
    download_url: z.string(),
});

export type ExportReadyEvent = z.infer<typeof ExportReadyEventSchema>;

// ---------------------------------------------------------------------------
// source_unavailable event
// ---------------------------------------------------------------------------

export const SourceUnavailableEventSchema = z.object({
    status: z.literal('unavailable'),
    source: z.string(),
    message: z.string(),
});

export type SourceUnavailableEvent = z.infer<typeof SourceUnavailableEventSchema>;

// ---------------------------------------------------------------------------
// Generic raw SSE event (name + raw JSON string)
// ---------------------------------------------------------------------------

export interface RawSSEEvent {
    name: SSEEventName;
    data: string;
}
