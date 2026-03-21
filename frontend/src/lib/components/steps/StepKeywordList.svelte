<svelte:options runes={true} />
<script lang="ts">
  import { Badge } from '$lib/components/ui/badge';

  let { data }: { data: { keywords?: string[] } } = $props();
  const keywords = $derived(data.keywords ?? []);
</script>

<div class="flex flex-col gap-2">
  <p class="text-sm text-muted-foreground">Refined keywords based on your description:</p>
  <div class="flex flex-wrap gap-2">
    {#each keywords as kw}
      <Badge variant="secondary">{kw}</Badge>
    {/each}
  </div>
</div>
