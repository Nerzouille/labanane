/**
 * Minimal SSE client that dispatches named events to typed callbacks.
 *
 * The server emits frames like:
 *   event: google_trends
 *   data: {...}
 *
 * We listen to each named event and forward the raw JSON string to callbacks.
 * Callers are responsible for parsing/validating the data with Zod.
 */

import type { ConnectionState, SSEEventName } from './types';

export type NamedEventCallback = (data: string) => void;

export interface SSECallbacks {
    onStateChange: (state: ConnectionState) => void;
    onError: (message: string) => void;
    onNamedEvent: (name: SSEEventName, data: string) => void;
}

/** All event names the server can emit. */
const eventNames: SSEEventName[] = [
    'google_trends',
    'marketplace_products',
    'export_ready',
    'source_unavailable',
];

/**
 * Opens an EventSource to `url`, wires up all named events, returns a cleanup fn.
 */
export function createSSEStream(url: string, callbacks: SSECallbacks): () => void {
    callbacks.onStateChange('connecting');

    const source = new EventSource(url);

    source.onopen = () => {
        callbacks.onStateChange('streaming');
    };

    // Register a listener for every known named event
    for (const name of eventNames) {
        source.addEventListener(name, (event: Event) => {
            if (event instanceof MessageEvent) {
                callbacks.onNamedEvent(name, event.data as string);
            }
        });
    }

    // The browser fires a generic error event both for connection drops and
    // for named "event: error" frames.
    source.addEventListener('error', (event: Event) => {
        if (event instanceof MessageEvent) {
            // Named server-sent error
            callbacks.onError((event.data as string) ?? 'Server error');
        } else {
            // Connection closed / backend unreachable → stream ended
            callbacks.onStateChange('done');
        }
        source.close();
    });

    return () => source.close();
}
