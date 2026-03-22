<svelte:options runes={true} />
<script lang="ts">
  import type { TimePoint } from '$lib/workflow-types';

  let { data, keyword }: { data: TimePoint[]; keyword: string } = $props();

  const maxVal = $derived(Math.max(...data.map((d) => d.value), 1));
  // Show up to 52 bars; downsample if more
  const bars = $derived(data.slice(-52));
</script>

<div class="flex flex-col gap-1">
  <p class="text-xs font-medium text-muted-foreground truncate">{keyword}</p>
  <div class="flex items-end gap-px h-10">
    {#each bars as point}
      {@const pct = (point.value / maxVal) * 100}
      {@const barColor = pct >= 70 ? 'bg-primary' : pct >= 30 ? 'bg-primary/60' : 'bg-primary/30'}
      <div
        class="flex-1 min-w-0 rounded-sm {barColor} transition-all"
        style="height: {Math.max(pct, 4)}%"
        title="{point.date}: {point.value}"
      ></div>
    {/each}
  </div>
  <div class="flex justify-between text-[10px] text-muted-foreground">
    {#if bars.length > 0}
      <span>{bars[0].date.slice(0, 7)}</span>
      <span>{bars[bars.length - 1].date.slice(0, 7)}</span>
    {/if}
  </div>
</div>
