<svelte:options runes={true} />
<script lang="ts">
  let { stepId }: { stepId: string } = $props();
</script>

{#if stepId === 'keyword_refinement'}
  <div class="flex flex-col gap-2">
    <div class="h-3.5 w-48 rounded bg-muted animate-pulse"></div>
    <div class="flex flex-wrap gap-2">
      {#each [80, 120, 96, 64, 108] as w}
        <div class="h-6 rounded-full bg-muted animate-pulse" style="width: {w}px"></div>
      {/each}
    </div>
  </div>

{:else if stepId === 'keyword_confirmation'}
  <div class="flex flex-col gap-3 items-center">
    <div class="h-4 w-64 rounded bg-muted animate-pulse"></div>
    <div class="flex gap-3">
      <div class="h-8 w-20 rounded bg-muted animate-pulse"></div>
      <div class="h-8 w-28 rounded bg-muted animate-pulse"></div>
    </div>
  </div>

{:else if stepId === 'product_research'}
  <div class="flex flex-col gap-2">
    <div class="h-3 w-28 rounded bg-muted animate-pulse"></div>
    {#each [0, 1, 2] as _}
      <div class="rounded-lg border border-border px-3 py-2.5 flex items-center gap-2.5">
        <div class="size-14 rounded-md bg-muted animate-pulse shrink-0"></div>
        <div class="flex flex-col gap-1.5 flex-1">
          <div class="h-3.5 w-3/4 rounded bg-muted animate-pulse"></div>
          <div class="h-3 w-16 rounded bg-muted animate-pulse"></div>
        </div>
      </div>
    {/each}
  </div>

{:else if stepId === 'market_research'}
  <div class="flex flex-col gap-2">
    {#each [0, 1, 2] as _}
      <div class="rounded-lg px-3 py-2.5 flex items-start gap-2.5">
        <div class="size-5 rounded bg-muted animate-pulse shrink-0 mt-0.5"></div>
        <div class="flex flex-col gap-1.5 flex-1">
          <div class="h-3.5 w-20 rounded bg-muted animate-pulse"></div>
          <div class="h-3 w-full rounded bg-muted animate-pulse"></div>
          <div class="h-3 w-4/5 rounded bg-muted animate-pulse"></div>
        </div>
      </div>
    {/each}
  </div>

{:else if stepId === 'final_criteria' || stepId === 'ai_analysis'}
  <div class="flex flex-col gap-3">
    <div class="flex items-stretch gap-3">
      <div class="size-24 rounded-lg bg-muted animate-pulse shrink-0"></div>
      <div class="flex-1 rounded-lg border border-border px-3 py-2.5 flex flex-col gap-2">
        <div class="h-4 w-16 rounded bg-muted animate-pulse"></div>
        <div class="h-3 w-full rounded bg-muted animate-pulse"></div>
        <div class="h-3 w-4/5 rounded bg-muted animate-pulse"></div>
      </div>
    </div>
    <div class="h-3 w-full rounded bg-muted animate-pulse"></div>
    <div class="h-3 w-5/6 rounded bg-muted animate-pulse"></div>
    <div class="flex flex-col gap-2 mt-1">
      {#each [0, 1, 2, 3, 4] as _}
        <div class="flex items-center gap-2">
          <div class="h-3 w-32 rounded bg-muted animate-pulse shrink-0"></div>
          <div class="flex-1 h-1.5 rounded-full bg-muted animate-pulse"></div>
          <div class="h-3 w-8 rounded bg-muted animate-pulse"></div>
        </div>
      {/each}
    </div>
  </div>

{:else if stepId === 'report_generation'}
  <div class="flex justify-center gap-3">
    <div class="h-9 w-28 rounded-md bg-muted animate-pulse"></div>
    <div class="h-9 w-36 rounded-md bg-muted animate-pulse"></div>
  </div>

{:else}
  <div class="flex flex-col gap-2">
    <div class="h-3.5 w-3/4 rounded bg-muted animate-pulse"></div>
    <div class="h-3 w-full rounded bg-muted animate-pulse"></div>
    <div class="h-3 w-5/6 rounded bg-muted animate-pulse"></div>
  </div>
{/if}
