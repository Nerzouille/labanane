import { SSEPayloadSchema, type SSEPayload, type ConnectionState } from './types';

export interface SSECallbacks {
    onEvent: (event: SSEPayload) => void;
    onStateChange: (state: ConnectionState) => void;
    onError: (message: string) => void;
}

/** Opens an EventSource, validates each message with Zod, returns a cleanup fn. */
export function createSSEStream(url: string, callbacks: SSECallbacks): () => void {
    callbacks.onStateChange('connecting');

    const source = new EventSource(url);

    source.onopen = () => {
        callbacks.onStateChange('streaming');
    };

    source.onmessage = (event: MessageEvent<string>) => {
        const parsed = SSEPayloadSchema.safeParse(JSON.parse(event.data));
        if (!parsed.success) {
            callbacks.onError(`Invalid payload: ${parsed.error.message}`);
            return;
        }
        callbacks.onEvent(parsed.data);
    };

    source.addEventListener('error', (event: Event) => {
        // Named 'error' SSE events come from the server (distinct from connection errors)
        if (event instanceof MessageEvent) {
            callbacks.onError(event.data ?? 'Server error');
        } else {
            // Connection dropped — stream ended or backend is down
            callbacks.onStateChange('done');
        }
        source.close();
    });

    return () => source.close();
}
