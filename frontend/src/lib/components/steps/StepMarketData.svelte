<script lang="ts">
  import * as Item from "$lib/components/ui/item/index.js";
  import { HugeiconsIcon } from "@hugeicons/svelte";
  import { ChartBarIncreasingIcon, BubbleChatDoneIcon, Alert02Icon, BarChartIcon } from "@hugeicons/core-free-icons";

  let { data }: {
    data: {
      sources_available?: string[];
      sources_unavailable?: string[];
      trend_summary?: string;
      sentiment_summary?: string;
    }
  } = $props();
</script>

<div class="flex flex-col gap-2">
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

  {#if data.trend_summary}
    <Item.Root variant="default" size="sm">
      <Item.Media>
        <HugeiconsIcon icon={ChartBarIncreasingIcon} class="s-5" />
      </Item.Media>
      <Item.Content>
        <Item.Title>Trends</Item.Title>
        <Item.Description>{data.trend_summary}</Item.Description>
      </Item.Content>
    </Item.Root>
  {/if}

  {#if data.sentiment_summary}
    <Item.Root variant="default" size="sm">
      <Item.Media>
        <HugeiconsIcon icon={BubbleChatDoneIcon} class="s-5" />
      </Item.Media>
      <Item.Content>
        <Item.Title>Community Sentiment</Item.Title>
        <Item.Description>{data.sentiment_summary}</Item.Description>
      </Item.Content>
    </Item.Root>
  {/if}

  {#if data.sources_available && data.sources_available.length}
    <Item.Root variant="default" size="sm">
      <Item.Media>
        <HugeiconsIcon icon={BarChartIcon} class="s-5" />
      </Item.Media>
      <Item.Content>
        <Item.Title>Sources</Item.Title>
        <Item.Description>{data.sources_available.join(', ')}</Item.Description>
      </Item.Content>
    </Item.Root>
  {/if}
</div>
