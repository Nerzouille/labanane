<svelte:options runes={true} />
<script lang="ts">
  import * as Item from '$lib/components/ui/item/index.js';
  import { Badge } from '$lib/components/ui/badge';
  import { HugeiconsIcon } from '@hugeicons/svelte';
  import { LinkSquare02Icon, ImageNotFoundIcon, StarIcon } from '@hugeicons/core-free-icons';
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
      products?: Array<{ title: string; price: string; url: string; image_url?: string; rating_stars?: number; rating_count?: number }>;
      is_final?: boolean;
    };
  } = $props();

  const products = $derived(data.products ?? []);

  function parsePrice(priceStr: string): number | null {
    if (!priceStr) return null;
    const cleaned = priceStr.replace(/\s/g, '').replace(/[^0-9.,]/g, '');
    if (!cleaned) return null;
    let numberStr = cleaned;
    if (numberStr.includes(',') && numberStr.includes('.')) {
        if (numberStr.indexOf(',') > numberStr.indexOf('.')) {
            numberStr = numberStr.replace(/\./g, '').replace(',', '.');
        } else {
            numberStr = numberStr.replace(/,/g, '');
        }
    } else if (numberStr.includes(',')) {
        numberStr = numberStr.replace(',', '.');
    }
    const val = parseFloat(numberStr);
    return isNaN(val) ? null : val;
  }

  const priceStats = $derived.by(() => {
    if (!isFinal || products.length === 0) return null;
    let min = Infinity, max = -Infinity, sum = 0, count = 0;
    
    for (const p of products) {
      const v = parsePrice(p.price);
      if (v !== null) {
        if (v < min) min = v;
        if (v > max) max = v;
        sum += v;
        count++;
      }
    }

    if (count === 0) return null;
    return {
      avg: (sum / count).toFixed(2),
      min: min.toFixed(2),
      max: max.toFixed(2)
    };
  });

  // Auto-scroll as new products arrive
  $effect(() => {
    const pLen = products.length;
    if (pLen > 0) {
      tick().then(() => {
        window.scrollTo({
          top: document.body.scrollHeight,
          behavior: 'smooth'
        });
      });
    }
  });
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
        <Item.Description class="text-emerald-700 font-bold">{p.price}</Item.Description>
        {#if p.rating_stars !== undefined && p.rating_count !== undefined}
          <div class="flex items-center gap-1 mt-1.5 text-xs text-yellow-600">
            <HugeiconsIcon icon={StarIcon} size={14} />
            <span class="font-bold">{p.rating_stars}</span>
            <span class="text-muted-foreground ml-0.5">({p.rating_count})</span>
          </div>
        {/if}
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

  {#if !isFinal}
    <div class="flex justify-center mt-6 py-4" in:fade>
      <Button disabled class="flex items-center gap-2 bg-muted/50 text-muted-foreground border-slate-200">
        <Spinner class="size-4" />
        Searching the web...
      </Button>
    </div>
  {:else if priceStats}
    <div in:fade={{ duration: 600 }} class="mt-6 border-t border-slate-200 pt-5 grid grid-cols-3 gap-3">
      <div class="flex flex-col items-center justify-center bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
        <span class="text-[0.65rem] uppercase font-bold text-muted-foreground tracking-wider mb-1">Moyenne</span>
        <span class="text-lg font-bold text-slate-800">{priceStats.avg} €</span>
      </div>
      <div class="flex flex-col items-center justify-center bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
        <span class="text-[0.65rem] uppercase font-bold text-muted-foreground tracking-wider mb-1">Prix Min</span>
        <span class="text-lg font-bold text-emerald-600">{priceStats.min} €</span>
      </div>
      <div class="flex flex-col items-center justify-center bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
        <span class="text-[0.65rem] uppercase font-bold text-muted-foreground tracking-wider mb-1">Prix Max</span>
        <span class="text-lg font-bold text-orange-600">{priceStats.max} €</span>
      </div>
    </div>
  {/if}
</div>
