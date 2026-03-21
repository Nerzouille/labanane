<svelte:options runes={true} />

<script lang="ts">
    import { createSSEStream } from '$lib/sse';
    import { GoogleTrendsEventSchema } from '$lib/types';
    import type { ConnectionState, RawSSEEvent, SSEEventName } from '$lib/types';
    import TrendsBlock from '$lib/components/TrendsBlock.svelte';

    // ------------------------------------------------------------------
    // Reactive state
    // ------------------------------------------------------------------

    // Single $state object — workaround for svelte-check 4.x bug where
    // $state() rune is only recognized when the variable name contains 'state'.
    let pageState = $state({
        conn: 'idle' as ConnectionState,
        keyword: '',
        errorMsg: '',
        events: [] as RawSSEEvent[],
    });

    let cleanup: (() => void) | null = null;

    // ------------------------------------------------------------------
    // Derived values
    // ------------------------------------------------------------------

    const isRunning = $derived(
        pageState.conn === 'connecting' || pageState.conn === 'streaming'
    );

    const trendsData = $derived.by(() => {
        const raw = pageState.events.find((e) => e.name === 'google_trends');
        if (!raw) return null;
        const parsed = GoogleTrendsEventSchema.safeParse(JSON.parse(raw.data));
        return parsed.success ? parsed.data : null;
    });

    const statusLabel = $derived(
        pageState.conn === 'connecting' ? 'Connexion…'
        : pageState.conn === 'streaming' ? 'Analyse en cours…'
        : pageState.conn === 'error'     ? pageState.errorMsg || 'Erreur'
        : pageState.conn === 'done'      ? 'Terminé'
        : ''
    );

    // ------------------------------------------------------------------
    // Handlers
    // ------------------------------------------------------------------

    function handleSubmit(e: SubmitEvent) {
        e.preventDefault();
        const kw = pageState.keyword.trim();
        if (!kw) return;
        startStream(kw);
    }

    function handleReset() {
        cleanup?.();
        cleanup = null;
        pageState.conn = 'idle';
        pageState.errorMsg = '';
        pageState.events = [];
    }

    function startStream(kw: string) {
        // Clean up any previous stream
        cleanup?.();
        pageState.errorMsg = '';
        pageState.events = [];

        cleanup = createSSEStream(`/api/stream?keyword=${encodeURIComponent(kw)}`, {
            onStateChange(conn) {
                pageState.conn = conn;
            },
            onError(msg) {
                pageState.errorMsg = msg;
                pageState.conn = 'error';
            },
            onNamedEvent(name: SSEEventName, data: string) {
                pageState.events = [...pageState.events, { name, data }];
            },
        });
    }

    // Cleanup on component destroy
    $effect(() => () => cleanup?.());
</script>

<main>
    <header>
        <h1>Trends Dashboard</h1>
        <p class="subtitle">Analyse Google Trends en temps réel</p>
    </header>

    <!-- Keyword form -->
    <form class="search-form" onsubmit={handleSubmit}>
        <input
            type="text"
            bind:value={pageState.keyword}
            placeholder="Entrez un mot-clé…"
            disabled={isRunning}
            class="keyword-input"
            aria-label="Mot-clé"
        />
        <button type="submit" disabled={isRunning || !pageState.keyword.trim()} class="btn-primary">
            {isRunning ? 'Analyse…' : 'Analyser'}
        </button>
        {#if pageState.conn !== 'idle'}
            <button type="button" onclick={handleReset} class="btn-secondary">
                Réinitialiser
            </button>
        {/if}
    </form>

    <!-- Status banner -->
    {#if statusLabel}
        <div class="status-banner" class:error={pageState.conn === 'error'}>
            {#if isRunning}
                <span class="spinner" aria-hidden="true"></span>
            {/if}
            {statusLabel}
        </div>
    {/if}

    <!-- Loading state: running but no trends data yet -->
    {#if isRunning && !trendsData}
        <div class="loading-placeholder">
            <span class="spinner large" aria-hidden="true"></span>
            <p>Récupération des données Google Trends…</p>
        </div>
    {/if}

    <!-- Trends dashboard blocks -->
    {#if trendsData}
        <TrendsBlock data={trendsData} />
    {/if}
</main>

<style>
    :global(body) {
        background: #020617;
        color: #e2e8f0;
        margin: 0;
        font-family: system-ui, -apple-system, sans-serif;
    }

    main {
        max-width: 1100px;
        margin: 0 auto;
        padding: 2rem 1.5rem 4rem;
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }

    header {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }

    h1 {
        font-size: 1.75rem;
        font-weight: 700;
        color: #f1f5f9;
        margin: 0;
    }

    .subtitle {
        font-size: 0.9rem;
        color: #64748b;
        margin: 0;
    }

    /* ------------------------------------------------------------------ */
    /* Search form                                                          */
    /* ------------------------------------------------------------------ */
    .search-form {
        display: flex;
        gap: 0.75rem;
        flex-wrap: wrap;
        align-items: center;
    }

    .keyword-input {
        flex: 1;
        min-width: 200px;
        max-width: 480px;
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-size: 1rem;
        color: #e2e8f0;
        outline: none;
        transition: border-color 0.15s;
    }

    .keyword-input:focus {
        border-color: #38bdf8;
    }

    .keyword-input::placeholder {
        color: #475569;
    }

    .keyword-input:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .btn-primary {
        background: #0ea5e9;
        color: #fff;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.4rem;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: background 0.15s;
    }

    .btn-primary:hover:not(:disabled) {
        background: #38bdf8;
    }

    .btn-primary:disabled {
        opacity: 0.45;
        cursor: not-allowed;
    }

    .btn-secondary {
        background: #1e293b;
        color: #94a3b8;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-size: 0.9rem;
        cursor: pointer;
        transition: background 0.15s;
    }

    .btn-secondary:hover {
        background: #334155;
        color: #e2e8f0;
    }

    /* ------------------------------------------------------------------ */
    /* Status banner                                                        */
    /* ------------------------------------------------------------------ */
    .status-banner {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.85rem;
        color: #94a3b8;
        padding: 0.5rem 0.75rem;
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 8px;
        width: fit-content;
    }

    .status-banner.error {
        color: #f87171;
        border-color: #7f1d1d;
        background: #1c0a0a;
    }

    /* ------------------------------------------------------------------ */
    /* Loading placeholder                                                  */
    /* ------------------------------------------------------------------ */
    .loading-placeholder {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
        padding: 3rem 0;
        color: #475569;
    }

    .loading-placeholder p {
        margin: 0;
        font-size: 0.9rem;
    }

    /* ------------------------------------------------------------------ */
    /* Spinner                                                              */
    /* ------------------------------------------------------------------ */
    .spinner {
        display: inline-block;
        width: 14px;
        height: 14px;
        border: 2px solid #334155;
        border-top-color: #38bdf8;
        border-radius: 50%;
        animation: spin 0.7s linear infinite;
        flex-shrink: 0;
    }

    .spinner.large {
        width: 36px;
        height: 36px;
        border-width: 3px;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }
</style>
