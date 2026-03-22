<svelte:options runes={true} />
<script lang="ts">
  import * as Item from '$lib/components/ui/item/index.js';
  import { Badge } from '$lib/components/ui/badge';
  import { HugeiconsIcon } from '@hugeicons/svelte';
  import { LinkSquare02Icon, ImageNotFoundIcon } from '@hugeicons/core-free-icons';
  import { fade, blur } from 'svelte/transition';

  function marketplaceLabel(url: string): string {
    try {
      const host = new URL(url).hostname.replace(/^www\./, '');
      const known: Record<string, string> = {
        'amazon.com': 'Amazon', 'amazon.fr': 'Amazon FR', 'amazon.co.uk': 'Amazon UK',
        'amazon.de': 'Amazon DE', 'ebay.com': 'eBay', 'etsy.com': 'Etsy',
        'walmart.com': 'Walmart', 'aliexpress.com': 'AliExpress',
      };
      return known[host] ?? host;
    } catch { return 'Unknown'; }
  }

  let { data }: {
    data: {
      products?: Array<{ title: string; price: string; url: string; image_url?: string }>;
    };
  } = $props();

  const products = $derived(data.products ?? []);

</script>

<div class="flex flex-col gap-2">
  <p class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
    {products.length} product{products.length !== 1 ? 's' : ''} found
  </p>

  {#each products as p (p.url + '-' + marketplaceLabel(p.url))}
    {@const marketplace = marketplaceLabel(p.url)}
    <div in:fade={{ duration: 1200, delay: 100 }} out:fade={{duration: 200}}>
      <Item.Root variant="outline" class="relative">
        <Badge variant="secondary" class="absolute top-2.5 right-3 text-xs font-mono">{marketplace}</Badge>

      <Item.Media variant="image" class="size-14 rounded-md">
        {#if p.image_url}
          <img src={p.image_url} alt={p.title} class="size-full object-contain" />
        {:else}
          <div class="size-full bg-muted flex items-center justify-center rounded-md">
            <HugeiconsIcon icon={ImageNotFoundIcon} class="s-5 text-muted-foreground/50" />
          </div>
        {/if}
      </Item.Media>

      <Item.Content>
        <Item.Title class="line-clamp-2 whitespace-normal">{p.title}</Item.Title>
        <Item.Description class="text-green-700 font-medium">{p.price}</Item.Description>
      </Item.Content>

      <a
        href={p.url}
        target="_blank"
        rel="noopener"
        class="absolute bottom-2 right-3 flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
      >
        View
        <HugeiconsIcon icon={LinkSquare02Icon} size={13} />
      </a>
    </Item.Root>
    </div>
  {/each}

</div>
