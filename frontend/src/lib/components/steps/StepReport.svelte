<svelte:options runes={true} />
<script lang="ts">
  import { Alert, AlertDescription } from '$lib/components/ui/alert';
  import { Button } from '$lib/components/ui/button';

  let { data }: { data: { run_id?: string; markdown_available?: boolean; note?: string } } = $props();
</script>

<div class="flex flex-col gap-3">
  <Alert class="border-green-500 bg-green-50 text-green-800">
    <AlertDescription>✓ Report generated</AlertDescription>
  </Alert>
  {#if data.run_id}
    <p class="text-sm text-muted-foreground">Run ID: <code class="font-mono text-xs bg-muted px-1 py-0.5 rounded">{data.run_id}</code></p>
  {/if}
  {#if data.note}
    <p class="text-sm text-muted-foreground italic">{data.note}</p>
  {/if}
  {#if data.markdown_available}
    <a href="/api/export/md?run_id={data.run_id}" class="inline-flex items-center justify-center rounded-md border border-border px-4 py-2 text-sm font-medium hover:bg-accent transition-colors">
      Export Markdown
    </a>
  {:else}
    <p class="text-sm text-muted-foreground italic">Export not yet available (stub).</p>
  {/if}
</div>
