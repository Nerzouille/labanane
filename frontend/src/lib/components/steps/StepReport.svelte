<script lang="ts">
  import { Button } from '$lib/components/ui/button';
  import { HugeiconsIcon } from '@hugeicons/svelte';
  import { FileEditIcon, Pdf01Icon, Copy01Icon, CheckmarkSquare01Icon } from '@hugeicons/core-free-icons';

  let { data }: { data: { run_id?: string; markdown_available?: boolean; note?: string } } = $props();

  let copied = $state(false);

  async function copyMarkdown() {
    const res = await fetch(`http://localhost:8000/api/export/${data.run_id}/markdown`);
    const text = await res.text();
    await navigator.clipboard.writeText(text);
    copied = true;
    setTimeout(() => (copied = false), 2000);
  }
</script>

<div class="flex flex-col gap-3">
  {#if data.markdown_available}
    <div class="flex flex-col items-center gap-3">
      <div class="flex items-center gap-3">
        <Button variant="outline" href="http://localhost:8000/api/export/{data.run_id}/pdf" target="_blank" rel="noopener" class="flex items-center gap-1.5">
          <HugeiconsIcon icon={Pdf01Icon} size={16} />
          Export PDF
        </Button>
        <Button href="http://localhost:8000/api/export/{data.run_id}/markdown" target="_blank" rel="noopener" class="flex items-center gap-1.5">
          <HugeiconsIcon icon={FileEditIcon} size={16} />
          Export Markdown
        </Button>
        <Button variant="outline" onclick={copyMarkdown} class="flex items-center gap-1.5">
          <HugeiconsIcon icon={copied ? CheckmarkSquare01Icon : Copy01Icon} size={16} />
          {copied ? 'Copied!' : 'Copy Markdown'}
        </Button>
      </div>
      {#if data.run_id}
        <p class="text-xs text-muted-foreground font-mono">{data.run_id}</p>
      {/if}
    </div>
  {:else}
    <p class="text-sm text-muted-foreground text-center">Report generation failed.</p>
  {/if}
</div>
