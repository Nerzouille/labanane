<svelte:options runes={true} />
<script lang="ts">
  import { Badge } from '$lib/components/ui/badge';
  import { Spinner } from '$lib/components/ui/spinner';

  let { data, tokens }: { data: { complete?: boolean; content?: string }; tokens?: string } = $props();
  const content = $derived(data.content ?? tokens ?? '');
  const isComplete = $derived(data.complete ?? false);
</script>

<div class="flex flex-col gap-2">
  {#if !isComplete && content === ''}
    <div class="flex items-center gap-2 text-muted-foreground text-sm">
      <Spinner class="w-4 h-4" />
      <span>Analysing…</span>
    </div>
  {/if}
  {#if content}
    <div class="bg-muted/30 border rounded-md p-3 {!isComplete ? 'border-primary' : 'border-border'}">
      <p class="text-sm leading-relaxed whitespace-pre-wrap">{content}</p>
    </div>
  {/if}
  {#if isComplete}
    <Badge variant="secondary" class="self-start">✓ Analysis complete</Badge>
  {/if}
</div>
