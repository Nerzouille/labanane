<svelte:options runes={true} />

<script lang="ts">
    import type { GoogleTrendsEvent } from '$lib/types';

    let { data }: { data: GoogleTrendsEvent } = $props();

    // ------------------------------------------------------------------
    // Constants
    // ------------------------------------------------------------------
    const PAD_H = 6;
    const PAD_TOP = 8;
    const PAD_BOTTOM = 24;
    const VIEW_W = 460;
    const VIEW_H = 110;
    const CHART_W = VIEW_W - PAD_H * 2;
    const CHART_H = VIEW_H - PAD_TOP - PAD_BOTTOM;

    const COLORS = [
        '#38bdf8', '#4ade80', '#fb923c', '#c084fc',
        '#2dd4bf', '#94a3b8', '#f472b6', '#facc15',
    ];

    // ------------------------------------------------------------------
    // Derived: line chart
    // ------------------------------------------------------------------
    const polylinePoints = $derived.by(() => {
        const pts = data.interest;
        if (pts.length === 0) return '';
        const maxVal = Math.max(...pts.map((p) => p.value), 1);
        return pts
            .map((p, i) => {
                const x = PAD_H + (i / Math.max(pts.length - 1, 1)) * CHART_W;
                const y = PAD_TOP + CHART_H - (p.value / maxVal) * CHART_H;
                return `${x.toFixed(1)},${y.toFixed(1)}`;
            })
            .join(' ');
    });

    // Area polygon: polyline points + bottom-right + bottom-left corners
    const areaPoints = $derived.by(() => {
        const pts = data.interest;
        if (pts.length === 0) return '';
        const maxVal = Math.max(...pts.map((p) => p.value), 1);
        const lineCoords = pts.map((p, i) => {
            const x = PAD_H + (i / Math.max(pts.length - 1, 1)) * CHART_W;
            const y = PAD_TOP + CHART_H - (p.value / maxVal) * CHART_H;
            return `${x.toFixed(1)},${y.toFixed(1)}`;
        });
        const lastX = (PAD_H + CHART_W).toFixed(1);
        const firstX = PAD_H.toFixed(1);
        const bottomY = (PAD_TOP + CHART_H).toFixed(1);
        return [...lineCoords, `${lastX},${bottomY}`, `${firstX},${bottomY}`].join(' ');
    });

    // Sample ~12 evenly-spaced points for month labels
    const labelPoints = $derived.by(() => {
        const pts = data.interest;
        if (pts.length === 0) return [] as Array<{ x: number; label: string }>;
        const count = Math.min(12, pts.length);
        const step = Math.max(1, Math.floor(pts.length / count));
        const result: Array<{ x: number; label: string }> = [];
        for (let i = 0; i < pts.length; i += step) {
            const p = pts[i];
            const x = PAD_H + (i / Math.max(pts.length - 1, 1)) * CHART_W;
            // p.date is "YYYY-MM-DD"; extract month abbreviation
            const d = new Date(p.date + 'T00:00:00');
            const label = d.toLocaleString('fr-FR', { month: 'short' });
            result.push({ x, label });
        }
        return result;
    });

    // ------------------------------------------------------------------
    // Derived: regions bar chart
    // ------------------------------------------------------------------
    const maxRegionValue = $derived(
        data.regions.length > 0 ? Math.max(...data.regions.map((r) => r.value), 1) : 1
    );

    const trendPositive = $derived(data.trend_pct >= 0);
    const trendLabel = $derived(
        (trendPositive ? '+' : '') + data.trend_pct + '% sur 12 mois'
    );
</script>

<div class="trends-grid">
    <!-- ============================================================ -->
    <!-- LEFT CARD — Évolution de l'intérêt                           -->
    <!-- ============================================================ -->
    <div class="card">
        <h2 class="card-title">Évolution de l'intérêt</h2>

        <div class="chips">
            <div class="chip">
                <span class="chip-label">Tendance</span>
                <span class="chip-value" class:positive={trendPositive} class:negative={!trendPositive}>
                    {trendLabel}
                </span>
            </div>
            <div class="chip">
                <span class="chip-label">Saisonnalité</span>
                <span class="chip-value neutral">{data.seasonality}</span>
            </div>
        </div>

        <!-- SVG line chart -->
        <svg
            viewBox="0 0 {VIEW_W} {VIEW_H}"
            width="100%"
            aria-label="Évolution de l'intérêt Google Trends"
            role="img"
            class="chart-svg"
        >
            <defs>
                <linearGradient id="area-gradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.35" />
                    <stop offset="100%" stop-color="#38bdf8" stop-opacity="0" />
                </linearGradient>
            </defs>

            <!-- Grid lines at 0 / 25 / 50 / 75 / 100 -->
            {#each [0, 25, 50, 75, 100] as level}
                <line
                    x1={PAD_H}
                    y1={PAD_TOP + CHART_H - (level / 100) * CHART_H}
                    x2={PAD_H + CHART_W}
                    y2={PAD_TOP + CHART_H - (level / 100) * CHART_H}
                    stroke="#1e293b"
                    stroke-width="1"
                />
            {/each}

            <!-- Area fill -->
            {#if areaPoints}
                <polygon points={areaPoints} fill="url(#area-gradient)" />
            {/if}

            <!-- Trend line -->
            {#if polylinePoints}
                <polyline
                    points={polylinePoints}
                    fill="none"
                    stroke="#38bdf8"
                    stroke-width="2"
                    stroke-linejoin="round"
                    stroke-linecap="round"
                />
            {/if}

            <!-- Month labels -->
            {#each labelPoints as lp (lp.x)}
                <text
                    x={lp.x}
                    y={VIEW_H - 6}
                    text-anchor="middle"
                    font-size="9"
                    fill="#64748b"
                >
                    {lp.label}
                </text>
            {/each}
        </svg>

        <p class="legend">&#9679; Intérêt (Google Trends)</p>
    </div>

    <!-- ============================================================ -->
    <!-- RIGHT CARD — Intérêt par région                              -->
    <!-- ============================================================ -->
    <div class="card">
        <h2 class="card-title">Intérêt par région</h2>

        <div class="chips">
            <div class="chip">
                <span class="chip-label">Top marché</span>
                <span class="chip-value market">{data.top_market} 🥇</span>
            </div>
            <div class="chip">
                <span class="chip-label">Opportunité</span>
                <span class="chip-value opportunity">{data.opportunity} ↗</span>
            </div>
        </div>

        <ul class="region-list">
            {#each data.regions as region, i (region.name)}
                <li class="region-row">
                    <span
                        class="dot"
                        style:background={COLORS[i % COLORS.length]}
                    ></span>
                    <span class="region-name">{region.name}</span>
                    <div class="bar-track">
                        <div
                            class="bar-fill"
                            style:width="{(region.value / maxRegionValue) * 100}%"
                            style:background={COLORS[i % COLORS.length]}
                        ></div>
                    </div>
                    <span class="region-value">{region.value}</span>
                </li>
            {/each}
        </ul>
    </div>
</div>

<style>
    /* ------------------------------------------------------------------ */
    /* Layout                                                               */
    /* ------------------------------------------------------------------ */
    .trends-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        width: 100%;
    }

    @media (max-width: 700px) {
        .trends-grid {
            grid-template-columns: 1fr;
        }
    }

    /* ------------------------------------------------------------------ */
    /* Card                                                                 */
    /* ------------------------------------------------------------------ */
    .card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.25rem 1.25rem 1rem;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }

    .card-title {
        font-size: 0.7rem;
        font-variant: small-caps;
        letter-spacing: 0.08em;
        color: #64748b;
        text-transform: uppercase;
        margin: 0;
        font-weight: 600;
    }

    /* ------------------------------------------------------------------ */
    /* Info chips                                                           */
    /* ------------------------------------------------------------------ */
    .chips {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }

    .chip {
        background: #1e293b;
        border-radius: 8px;
        padding: 0.35rem 0.75rem;
        display: flex;
        flex-direction: column;
        gap: 0.1rem;
    }

    .chip-label {
        font-size: 0.65rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .chip-value {
        font-size: 0.9rem;
        font-weight: 700;
        color: #e2e8f0;
    }

    .chip-value.positive { color: #4ade80; }
    .chip-value.negative { color: #f87171; }
    .chip-value.neutral  { color: #e2e8f0; }
    .chip-value.market   { color: #e2e8f0; font-size: 1rem; }
    .chip-value.opportunity { color: #38bdf8; }

    /* ------------------------------------------------------------------ */
    /* SVG chart                                                            */
    /* ------------------------------------------------------------------ */
    .chart-svg {
        display: block;
        width: 100%;
        height: auto;
    }

    .legend {
        font-size: 0.7rem;
        color: #475569;
        margin: 0;
    }

    /* ------------------------------------------------------------------ */
    /* Region list                                                          */
    /* ------------------------------------------------------------------ */
    .region-list {
        list-style: none;
        padding: 0;
        margin: 0;
        display: flex;
        flex-direction: column;
        gap: 0.45rem;
    }

    .region-row {
        display: grid;
        grid-template-columns: 10px 110px 1fr 32px;
        align-items: center;
        gap: 0.5rem;
    }

    .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        flex-shrink: 0;
    }

    .region-name {
        font-size: 0.78rem;
        color: #cbd5e1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .bar-track {
        height: 6px;
        background: #1e293b;
        border-radius: 99px;
        overflow: hidden;
    }

    .bar-fill {
        height: 100%;
        border-radius: 99px;
        transition: width 0.5s ease;
    }

    .region-value {
        font-size: 0.78rem;
        color: #94a3b8;
        text-align: right;
    }
</style>
