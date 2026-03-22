<svelte:options runes={true} />
<script lang="ts">
  import type { TimePoint } from '$lib/workflow-types';
  import * as Chart from '$lib/components/ui/chart/index.js';
  import { scaleUtc } from 'd3-scale';
  import { Area, AreaChart, ChartClipPath } from 'layerchart';
  import { curveMonotoneX } from 'd3-shape';
  import { cubicInOut } from 'svelte/easing';

  let { data, keyword }: { data: TimePoint[]; keyword: string } = $props();

  // Moyenne mobile sur 4 semaines pour lisser les pics
  const chartData = $derived.by(() => {
    const pts = data.slice(-52);
    const W = 4;
    return pts.map((d, i) => {
      const slice = pts.slice(Math.max(0, i - W + 1), i + 1);
      const avg = slice.reduce((s, p) => s + p.value, 0) / slice.length;
      return { date: new Date(d.date), value: Math.round(avg) };
    });
  });

  const chartConfig = {
    value: { label: keyword, color: '#3b82f6' },
  } satisfies Chart.ChartConfig;
</script>

<Chart.Container config={chartConfig} class="aspect-auto h-[160px] w-full">
  <AreaChart
    data={chartData}
    x="date"
    xScale={scaleUtc()}
    series={[{ key: 'value', label: keyword, color: chartConfig.value.color }]}
    props={{
      area: {
        curve: curveMonotoneX,
        'fill-opacity': 0.4,
        line: { class: 'stroke-1' },
        motion: 'tween',
      },
      xAxis: {
        format: (v: Date) => v.toLocaleDateString('fr-FR', { month: 'short', year: '2-digit' }),
      },
      yAxis: { format: () => '' },
    }}
  >
    {#snippet marks({ series, getAreaProps })}
      <defs>
        <linearGradient id="fillInterest" x1="0" y1="0" x2="0" y2="1">
          <stop offset="5%"  stop-color="var(--color-value)" stop-opacity={1.0} />
          <stop offset="95%" stop-color="var(--color-value)" stop-opacity={0.05} />
        </linearGradient>
      </defs>
      <ChartClipPath
        initialWidth={0}
        motion={{ width: { type: 'tween', duration: 1000, easing: cubicInOut } }}
      >
        {#each series as s, i (s.key)}
          <Area {...getAreaProps(s, i)} fill="url(#fillInterest)" />
        {/each}
      </ChartClipPath>
    {/snippet}
    {#snippet tooltip()}
      <Chart.Tooltip
        labelFormatter={(v: Date) => v.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })}
        indicator="line"
      />
    {/snippet}
  </AreaChart>
</Chart.Container>
