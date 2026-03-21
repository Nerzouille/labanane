<script lang="ts">
  import * as Item from "$lib/components/ui/item/index.js";
  import { HugeiconsIcon } from "@hugeicons/svelte";
  import { Tick02Icon, Cancel01Icon, Alert02Icon, CheckmarkBadge01Icon, InformationCircleIcon } from "@hugeicons/core-free-icons";

  let { data }: {
    data: {
      summary?: string;
      go_no_go?: 'go' | 'no-go' | 'conditional';
      key_risks?: string[];
      key_opportunities?: string[];
    }
  } = $props();

  const verdict = $derived(data.go_no_go ?? 'conditional');
  const verdictIcon = $derived(
    verdict === 'go' ? Tick02Icon :
    verdict === 'no-go' ? Cancel01Icon :
    Alert02Icon
  );
  const verdictLabel = $derived(
    verdict === 'go' ? 'Go' : verdict === 'no-go' ? 'No-Go' : 'Conditional'
  );
  const verdictIconClass = $derived(
    verdict === 'go' ? 'text-green-600' :
    verdict === 'no-go' ? 'text-red-600' :
    'text-yellow-600'
  );
  const verdictItemClass = $derived(
    verdict === 'go' ? 'border-green-500/40 bg-green-500/10' :
    verdict === 'no-go' ? 'border-red-500/40 bg-red-500/10' :
    'border-yellow-500/40 bg-yellow-500/10'
  );
  const verdictTitleClass = $derived(
    verdict === 'go' ? 'text-green-700' :
    verdict === 'no-go' ? 'text-red-700' :
    'text-yellow-700'
  );
</script>

<div class="flex flex-col gap-2">
  <Item.Root variant="outline" size="sm" class={verdictItemClass}>
    <Item.Media>
      <HugeiconsIcon icon={verdictIcon} class="s-5 {verdictIconClass}" />
    </Item.Media>
    <Item.Content>
      <Item.Title class={verdictTitleClass}>{verdictLabel}</Item.Title>
      {#if data.summary}
        <Item.Description>{data.summary}</Item.Description>
      {/if}
    </Item.Content>
  </Item.Root>

  {#if data.key_opportunities && data.key_opportunities.length}
    {#each data.key_opportunities as o}
      <Item.Root variant="default" size="sm">
        <Item.Media>
          <HugeiconsIcon icon={CheckmarkBadge01Icon} class="s-5 text-green-600" />
        </Item.Media>
        <Item.Content>
          <Item.Title>{o}</Item.Title>
        </Item.Content>
      </Item.Root>
    {/each}
  {/if}

  {#if data.key_risks && data.key_risks.length}
    {#each data.key_risks as r}
      <Item.Root variant="default" size="sm">
        <Item.Media>
          <HugeiconsIcon icon={InformationCircleIcon} class="s-5 text-destructive" />
        </Item.Media>
        <Item.Content>
          <Item.Title>{r}</Item.Title>
        </Item.Content>
      </Item.Root>
    {/each}
  {/if}
</div>
