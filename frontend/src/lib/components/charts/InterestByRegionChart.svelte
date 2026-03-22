<svelte:options runes={true} />
<script lang="ts">
  import type { RegionPoint } from '$lib/workflow-types';

  let { data }: { data: RegionPoint[] } = $props();

  const top = $derived([...data].sort((a, b) => b.value - a.value).slice(0, 8));
  const maxVal = $derived(Math.max(...top.map((d) => d.value), 1));
</script>

<div class="flex flex-col gap-1.5">
  {#each top as point}
    {@const pct = (point.value / maxVal) * 100}
    <div class="flex items-center gap-2">
      <span class="text-xs text-muted-foreground w-24 shrink-0 truncate" title={point.name}>{point.name}</span>
      <div class="flex-1 h-1.5 rounded-full bg-muted/40">
        <div class="h-full rounded-full bg-primary/70 transition-all" style="width: {pct}%"></div>
      </div>
      <span class="text-xs tabular-nums w-8 text-right text-muted-foreground">{point.value}</span>
    </div>
  {/each}
</div>
