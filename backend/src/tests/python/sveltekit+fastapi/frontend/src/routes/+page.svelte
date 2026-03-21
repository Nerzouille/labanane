<svelte:options runes={true} />

<script lang="ts">
    import { createSSEStream } from '$lib/sse';
    import type { SSEPayload, ConnectionState } from '$lib/types';

    // Single $state object — workaround for svelte-check 4.4.5 bug where
    // $state() rune detection requires the variable name to include 'state'.
    let state = $state({
        conn: 'idle' as ConnectionState,
        progress: 0,
        currentTask: '',
        errorMsg: '',
        events: [] as SSEPayload[],
    });

    let cleanup: (() => void) | null = null;

    const statusLabel = $derived(
        state.conn === 'streaming' ? state.currentTask || 'Streaming…'
        : state.conn === 'error'   ? state.errorMsg || 'Error'
        : state.conn === 'done'    ? 'Done'
        : state.conn === 'connecting' ? 'Connecting…'
        : 'Ready'
    );

    function startStream() {
        cleanup?.();
        state.progress = 0;
        state.currentTask = '';
        state.errorMsg = '';
        state.events = [];

        cleanup = createSSEStream('/api/sse', {
            onEvent(event) {
                state.progress = event.percentage;
                state.currentTask = event.message;
                state.events = [...state.events, event];
            },
            onStateChange(conn) {
                state.conn = conn;
            },
            onError(msg) {
                state.errorMsg = msg;
                state.conn = 'error';
            },
        });
    }

    $effect(() => () => cleanup?.());
</script>

<main>
    <h1>SSE Stream Demo</h1>
    <p class="subtitle">SvelteKit BFF proxy → FastAPI</p>

    <button
        onclick={startStream}
        disabled={state.conn === 'connecting' || state.conn === 'streaming'}
    >
        {state.conn === 'streaming' ? 'Streaming…' : 'Start Stream'}
    </button>

    <div class="progress-container">
        <p class="status">Status: <strong>{statusLabel}</strong></p>
        <div
            class="bar"
            role="progressbar"
            aria-valuenow={state.progress}
            aria-valuemin={0}
            aria-valuemax={100}
        >
            <div class="fill" style:width="{state.progress}%"></div>
        </div>
        <p class="pct">{Math.round(state.progress)}%</p>
    </div>

    {#if state.errorMsg}
        <p class="error">{state.errorMsg}</p>
    {/if}

    {#if state.events.length > 0}
        <h3>Events ({state.events.length})</h3>
        <ul>
            {#each state.events as e (e.id)}
                <li>
                    <span class="badge">{e.status}</span>
                    #{e.id} — {e.message} <em>({e.percentage}%)</em>
                </li>
            {/each}
        </ul>
    {/if}
</main>

<style>
    main {
        max-width: 600px;
        margin: 2rem auto;
        font-family: sans-serif;
        padding: 1rem;
    }

    .subtitle { color: #666; margin-top: -0.5rem; }

    button {
        padding: 0.5rem 1.25rem;
        font-size: 1rem;
        cursor: pointer;
        border: none;
        border-radius: 6px;
        background: #ff3e00;
        color: white;
        margin-bottom: 1.5rem;
    }

    button:disabled { opacity: 0.5; cursor: not-allowed; }

    .progress-container { margin-bottom: 1rem; }

    .bar {
        width: 100%;
        background: #eee;
        height: 20px;
        border-radius: 10px;
        margin: 0.5rem 0;
        overflow: hidden;
    }

    .fill {
        height: 100%;
        background: #ff3e00;
        transition: width 0.3s ease;
        border-radius: 10px;
    }

    .pct { font-size: 0.85rem; color: #555; }

    .error { color: #c00; background: #fee; padding: 0.5rem; border-radius: 4px; }

    ul { list-style: none; padding: 0; }

    li {
        padding: 0.4rem 0;
        border-bottom: 1px solid #eee;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9rem;
    }

    .badge {
        font-size: 0.7rem;
        background: #ff3e00;
        color: white;
        padding: 0.1rem 0.4rem;
        border-radius: 4px;
        text-transform: uppercase;
    }
</style>
