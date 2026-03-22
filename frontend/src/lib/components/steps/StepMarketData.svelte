<svelte:options runes={true} />
<script lang="ts">
  import * as Item from "$lib/components/ui/item/index.js";
  import { HugeiconsIcon } from "@hugeicons/svelte";
  import { Alert02Icon, ChartBarIncreasingIcon } from "@hugeicons/core-free-icons";
  import InterestOverTimeChart from "$lib/components/charts/InterestOverTimeChart.svelte";
  import InterestByRegionChart from "$lib/components/charts/InterestByRegionChart.svelte";
  import RelatedQueriesChart from "$lib/components/charts/RelatedQueriesChart.svelte";
  import type { KeywordTrends } from "$lib/workflow-types";

  let { data }: {
    data: {
      keywords?: string[];
      sources_available?: string[];
      sources_unavailable?: string[];
      trends?: Record<string, KeywordTrends>;
    }
  } = $props();

  const trendEntries = $derived(
    Object.entries(data.trends ?? {}).filter(([, t]) => t.interest_over_time.length > 0)
  );
  const activekw = $derived(trendEntries.map(([kw]) => kw));
</script>

<div class="flex flex-col gap-3">

  {#if data.sources_unavailable && data.sources_unavailable.length > 0}
    <Item.Root variant="outline" size="sm" class="border-yellow-500/40 bg-yellow-500/10">
      <Item.Media>
        <HugeiconsIcon icon={Alert02Icon} class="s-5 text-yellow-600" />
      </Item.Media>
      <Item.Content>
        <Item.Title class="text-yellow-700">Some sources unavailable</Item.Title>
        <Item.Description>{data.sources_unavailable.join(', ')}</Item.Description>
      </Item.Content>
    </Item.Root>
  {/if}

  {#if trendEntries.length > 0}

    <!-- Interest over time per keyword -->
    <div class="rounded-lg border bg-card p-3 flex flex-col gap-3">
      <div class="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
        <HugeiconsIcon icon={ChartBarIncreasingIcon} class="s-4" />
        Interest over time
      </div>
      <div class="flex flex-col gap-4">
        {#each trendEntries as [kw, trends]}
          {#if trends.interest_over_time.length > 0}
            <InterestOverTimeChart data={trends.interest_over_time} keyword={kw} />
          {/if}
        {/each}
      </div>
    </div>

    <!-- Interest by region — show for first keyword with data -->
    {#each trendEntries.slice(0, 1) as [kw, trends]}
      {#if trends.interest_by_region.length > 0}
        <div class="rounded-lg border bg-card p-3 flex flex-col gap-2">
          <p class="text-xs font-medium text-muted-foreground">Top regions — {kw}</p>
          <InterestByRegionChart data={trends.interest_by_region} />
        </div>
      {/if}
    {/each}

    <!-- Related queries — aggregate across keywords -->
    {#each trendEntries.slice(0, 1) as [kw, trends]}
      {#if trends.related_queries_top.length > 0 || trends.related_queries_rising.length > 0}
        <div class="rounded-lg border bg-card p-3 flex flex-col gap-2">
          <p class="text-xs font-medium text-muted-foreground">Related searches — {kw}</p>
          <RelatedQueriesChart top={trends.related_queries_top} rising={trends.related_queries_rising} />
        </div>
      {/if}
    {/each}

  {:else if data.sources_available && data.sources_available.length === 0}
    <p class="text-sm text-muted-foreground text-center">No trend data available.</p>
  {/if}

  {#if data.sources_available && data.sources_available.length > 0}
    <p class="text-xs text-muted-foreground">Sources: {data.sources_available.join(', ')}</p>
  {/if}

</div>
