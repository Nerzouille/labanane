<svelte:options runes={true} />
<script lang="ts">
  import { Alert, AlertDescription } from '$lib/components/ui/alert';
  import { Separator } from '$lib/components/ui/separator';
  import { Badge } from '$lib/components/ui/badge';

  let { data }: {
    data: {
      sources_available?: string[];
      sources_unavailable?: string[];
      trend_summary?: string;
      sentiment_summary?: string;
    }
  } = $props();
</script>

<div class="flex flex-col gap-3">
  {#if data.sources_unavailable && data.sources_unavailable.length > 0}
    <Alert class="border-yellow-400 bg-yellow-50 text-yellow-800">
      <AlertDescription>⚠ Some sources unavailable: {data.sources_unavailable.join(', ')}</AlertDescription>
    </Alert>
  {/if}

  {#if data.trend_summary}
    <div>
      <p class="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-1">Trends</p>
      <p class="text-sm">{data.trend_summary}</p>
    </div>
  {/if}

  {#if data.trend_summary && data.sentiment_summary}
    <Separator />
  {/if}

  {#if data.sentiment_summary}
    <div>
      <p class="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-1">Community Sentiment</p>
      <p class="text-sm">{data.sentiment_summary}</p>
    </div>
  {/if}

  <div class="flex flex-wrap gap-1">
    {#each (data.sources_available ?? []) as src}
      <Badge variant="outline" class="text-xs">{src}</Badge>
    {/each}
  </div>
</div>
