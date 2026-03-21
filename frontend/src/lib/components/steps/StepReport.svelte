<svelte:options runes={true} />
<script lang="ts">
  import { Alert, AlertDescription } from '$lib/components/ui/alert';
  import { Button } from '$lib/components/ui/button';
  import { HugeiconsIcon } from '@hugeicons/svelte';
  import { Tick02Icon, FileEditIcon, Pdf01Icon } from '@hugeicons/core-free-icons';

  let { data }: { data: { run_id?: string; markdown_available?: boolean; note?: string } } = $props();
</script>

<div class="flex flex-col gap-3">
  <Alert class="border-green-500 bg-green-50 text-green-800">
    <AlertDescription class="flex items-center gap-1.5">
      <HugeiconsIcon icon={Tick02Icon} size={15} />
      Report generated
    </AlertDescription>
  </Alert>
  {#if data.run_id}
    <p class="text-sm text-muted-foreground">Run ID: <code class="font-mono text-xs bg-muted px-1 py-0.5 rounded">{data.run_id}</code></p>
  {/if}
  {#if data.note}
    <p class="text-sm text-muted-foreground italic">{data.note}</p>
  {/if}
  {#if data.markdown_available}
    <div class="flex items-center gap-3 justify-end">
      <Button variant="outline" href="/api/export/pdf?run_id={data.run_id}" class="flex items-center gap-1.5">
        <HugeiconsIcon icon={Pdf01Icon} size={16} />
        Export PDF
      </Button>
      <Button href="/api/export/md?run_id={data.run_id}" class="flex items-center gap-1.5">
        <HugeiconsIcon icon={FileEditIcon} size={16} />
        Export Markdown
      </Button>
    </div>
  {:else}
    <p class="text-sm text-muted-foreground italic">Export not yet available (stub).</p>
  {/if}
</div>
