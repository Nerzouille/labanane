<svelte:options runes={true} />
<script lang="ts">
  import type { QueryPoint, RisingPoint } from '$lib/workflow-types';

  let {
    top = [],
    rising = [],
  }: { top?: QueryPoint[]; rising?: RisingPoint[] } = $props();

  const maxVal = $derived(Math.max(...top.map((d) => d.value), 1));
  const topSlice = $derived(top.slice(0, 6));
</script>

<div class="flex flex-col gap-2">
  {#if topSlice.length > 0}
    <p class="text-xs font-medium text-muted-foreground">Top searches</p>
    <div class="flex flex-col gap-1.5">
      {#each topSlice as item}
        {@const pct = (item.value / maxVal) * 100}
        <div class="flex items-center gap-2">
          <span class="text-xs text-muted-foreground w-28 shrink-0 truncate" title={item.query}>{item.query}</span>
          <div class="flex-1 h-1.5 rounded-full bg-muted/40">
            <div class="h-full rounded-full bg-blue-500/70 transition-all" style="width: {pct}%"></div>
          </div>
          <span class="text-xs tabular-nums w-8 text-right text-muted-foreground">{item.value}</span>
        </div>
      {/each}
    </div>
  {/if}

  {#if rising.length > 0}
    <p class="text-xs font-medium text-muted-foreground mt-1">Rising searches</p>
    <div class="flex flex-wrap gap-1">
      {#each rising.slice(0, 6) as item}
        <span class="inline-flex items-center rounded-full border px-2 py-0.5 text-xs text-muted-foreground">
          {item.query}
          {#if item.value !== 'Breakout'}
            <span class="ml-1 text-green-600">↑{item.value}</span>
          {:else}
            <span class="ml-1 text-green-600">🚀</span>
          {/if}
        </span>
      {/each}
    </div>
  {/if}
</div>
