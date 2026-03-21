<script lang="ts">
  import * as Item from "$lib/components/ui/item/index.js";
  import { Spinner } from '$lib/components/ui/spinner';
  import { HugeiconsIcon } from "@hugeicons/svelte";
  import { Tick02Icon } from "@hugeicons/core-free-icons";
  let { data, tokens }: { data: { complete?: boolean; content?: string }; tokens?: string } = $props();
  const content = $derived(data.content ?? tokens ?? '');
  const isComplete = $derived(data.complete ?? false);
</script>

<div class="flex flex-col gap-2">
  {#if !isComplete && content === ''}
    <Item.Root variant="outline" size="sm">
      <Item.Media>
        <Spinner class="s-5" />
      </Item.Media>
      <Item.Content>
        <Item.Title>Analysing…</Item.Title>
      </Item.Content>
    </Item.Root>
  {/if}
  {#if content}
    <Item.Root variant="outline" size="sm">
      <Item.Content>
        <Item.Title>{content}</Item.Title>
      </Item.Content>
    </Item.Root>
  {/if}
  {#if isComplete}
    <Item.Root variant="outline" size="sm">
      <Item.Media>
        <HugeiconsIcon icon={Tick02Icon} class="s-5" />
      </Item.Media>
    </Item.Root>
  {/if}
</div>
