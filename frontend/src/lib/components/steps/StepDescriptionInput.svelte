<svelte:options runes={true} />
<script lang="ts">
  import { Button } from '$lib/components/ui/button';
  import { Textarea } from '$lib/components/ui/textarea';

  let { data, onAction }: { data: { text?: string }; onAction: (a: object) => void } = $props();
  let description = $state('')
  $effect(() => { description = data.text ?? ''; });

  function submit(e: SubmitEvent) {
    e.preventDefault();
    if (!description.trim()) return;
    onAction({ type: 'user_input', data: { description } });
  }
</script>

<div class="flex flex-col gap-3">
  <p class="text-sm text-muted-foreground">Describe the product you want to analyse.</p>
  <form onsubmit={submit} class="flex flex-col gap-2">
    <Textarea
      bind:value={description}
      placeholder="e.g. ergonomic desk mats for remote workers"
      rows={3}
    />
    <Button type="submit" disabled={!description.trim()} class="self-start">Continue →</Button>
  </form>
</div>
