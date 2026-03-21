<svelte:options runes={true} />
<script lang="ts">
  let { data }: { data: { products?: Array<{title: string; price: string; url: string}> } } = $props();
  const products = $derived(data.products ?? []);
</script>

<div class="flex flex-col gap-2">
  <p class="text-sm text-muted-foreground">{products.length} product{products.length !== 1 ? 's' : ''} found:</p>
  <div class="flex flex-col gap-2">
    {#each products as p}
      <div class="flex items-center gap-3 px-3 py-2 bg-muted/30 border border-border rounded-md">
        <span class="flex-1 font-medium text-sm">{p.title}</span>
        <span class="text-green-700 text-sm font-medium">{p.price}</span>
        <a href={p.url} target="_blank" rel="noopener" class="text-sm text-primary hover:underline">View →</a>
      </div>
    {/each}
  </div>
</div>
