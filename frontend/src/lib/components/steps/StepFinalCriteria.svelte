<svelte:options runes={true} />
<script lang="ts">
  import { Badge } from '$lib/components/ui/badge';
  import { Separator } from '$lib/components/ui/separator';

  let { data }: {
    data: {
      summary?: string;
      go_no_go?: 'go' | 'no-go' | 'conditional';
      key_risks?: string[];
      key_opportunities?: string[];
    }
  } = $props();

  const verdict = $derived(data.go_no_go ?? 'conditional');
  const verdictVariant = $derived(
    verdict === 'go' ? 'default' as const :
    verdict === 'no-go' ? 'destructive' as const :
    'secondary' as const
  );
  const verdictLabel = $derived(
    verdict === 'go' ? '✓ Go' : verdict === 'no-go' ? '✗ No-Go' : '⚠ Conditional'
  );
</script>

<div class="flex flex-col gap-3">
  <Badge variant={verdictVariant} class="self-start text-sm px-3 py-1">{verdictLabel}</Badge>

  {#if data.summary}
    <p class="text-sm">{data.summary}</p>
  {/if}

  {#if (data.key_opportunities && data.key_opportunities.length) || (data.key_risks && data.key_risks.length)}
    <Separator />
  {/if}

  {#if data.key_opportunities && data.key_opportunities.length}
    <div>
      <p class="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-1">Opportunities</p>
      <ul class="list-disc pl-4 flex flex-col gap-0.5">
        {#each data.key_opportunities as o}
          <li class="text-sm">{o}</li>
        {/each}
      </ul>
    </div>
  {/if}

  {#if data.key_risks && data.key_risks.length}
    <div>
      <p class="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-1">Risks</p>
      <ul class="list-disc pl-4 flex flex-col gap-0.5">
        {#each data.key_risks as r}
          <li class="text-sm">{r}</li>
        {/each}
      </ul>
    </div>
  {/if}
</div>
