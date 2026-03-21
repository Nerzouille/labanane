/**
 * GET /api/stream?keyword=<keyword>
 *
 * SvelteKit BFF proxy: forwards the request to FastAPI and pipes the
 * SSE stream back to the browser. The browser never talks to FastAPI directly.
 */

import type { RequestHandler } from './$types';

const BACKEND_BASE = 'http://localhost:8000';

export const GET: RequestHandler = async ({ url }) => {
    const keyword = url.searchParams.get('keyword') ?? '';
    const backendUrl = `${BACKEND_BASE}/stream?keyword=${encodeURIComponent(keyword)}`;

    let response: Response;

    try {
        response = await fetch(backendUrl);
    } catch {
        return new Response(
            'event: error\ndata: {"status":"error","message":"Backend unreachable"}\n\n',
            {
                status: 502,
                headers: { 'Content-Type': 'text/event-stream' },
            },
        );
    }

    if (!response.ok || !response.body) {
        return new Response(
            'event: error\ndata: {"status":"error","message":"Backend error"}\n\n',
            {
                status: 502,
                headers: { 'Content-Type': 'text/event-stream' },
            },
        );
    }

    const upstream = response.body;

    const stream = new ReadableStream({
        start(controller) {
            const reader = upstream.getReader();

            function push() {
                reader
                    .read()
                    .then(({ done, value }) => {
                        if (done) {
                            controller.close();
                            return;
                        }
                        controller.enqueue(value);
                        push();
                    })
                    .catch((err: unknown) => {
                        controller.error(err);
                    });
            }

            push();
        },
        cancel() {
            upstream.cancel();
        },
    });

    return new Response(stream, {
        headers: {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',
        },
    });
};
