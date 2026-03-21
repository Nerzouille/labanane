<script lang="ts">
  import * as Chart from "$lib/components/ui/chart/index.js";
  import { ArcChart, Text } from "layerchart";

  let { score }: { score: number } = $props();

  const scoreColor = $derived(
    score >= 70 ? 'var(--color-score-high)' :
    score >= 40 ? 'var(--color-score-mid)' :
    'var(--color-score-low)'
  );
  const scoreLabel = $derived(
    score >= 70 ? 'Strong' : score >= 40 ? 'Moderate' : 'Weak'
  );

  const chartConfig = $derived({
    score: { label: 'Viability', color: scoreColor },
  } satisfies Chart.ChartConfig);

  const chartData = $derived([
    { key: 'score', label: 'Viability', value: score, color: scoreColor },
  ]);
</script>

<div
  class="shrink-0 w-24 overflow-hidden rounded-lg border bg-card flex flex-col items-center pb-2"
  style="--color-score-high: #16a34a; --color-score-mid: #ca8a04; --color-score-low: #dc2626;"
>
  <div class="w-full aspect-square overflow-hidden flex items-center justify-center">
    <Chart.Container config={chartConfig} class="w-full h-full aspect-square">
      <ArcChart
        data={chartData}
        label="label"
        value="value"
        outerRadius={-10}
        innerRadius={-8}
        padding={8}
        range={[90, -270]}
        maxValue={100}
        cornerRadius={8}
        series={chartData.map((d) => ({
          key: d.key,
          color: d.color,
          data: [d],
        }))}
        props={{
          arc: { track: { fill: "var(--muted)" }, motion: "tween" },
        }}
        tooltip={false}
      >
        {#snippet belowMarks()}
          <circle cx="0" cy="0" r="36" class="fill-background" />
        {/snippet}
        {#snippet aboveMarks()}
          <Text
            value={String(score)}
            textAnchor="middle"
            verticalAnchor="middle"
            class="fill-foreground text-xl! font-bold"
          />
        {/snippet}
      </ArcChart>
    </Chart.Container>
  </div>
  <p class="text-xs text-muted-foreground leading-none">{scoreLabel}</p>
</div>
