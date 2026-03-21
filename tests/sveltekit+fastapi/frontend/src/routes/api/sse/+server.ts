import type { RequestHandler } from './$types';

const BACKEND_URL = 'http://localhost:8000/stream';

export const GET: RequestHandler = async () => {
    let response: Response;

    try {
        response = await fetch(BACKEND_URL);
    } catch {
        return new Response('data: {"status":"error","message":"Backend unreachable"}\n\n', {
            status: 502,
            headers: { 'Content-Type': 'text/event-stream' },
        });
    }

    if (!response.ok || !response.body) {
        return new Response('data: {"status":"error","message":"Backend error"}\n\n', {
            status: 502,
            headers: { 'Content-Type': 'text/event-stream' },
        });
    }

    const upstream = response.body;

    const stream = new ReadableStream({
        start(controller) {
            const reader = upstream.getReader();

            function push() {
                reader.read().then(({ done, value }) => {
                    if (done) {
                        controller.close();
                        return;
                    }
                    controller.enqueue(value);
                    push();
                }).catch((err: unknown) => {
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
