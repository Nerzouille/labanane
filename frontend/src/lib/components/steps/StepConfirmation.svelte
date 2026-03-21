<svelte:options runes={true} />
<script lang="ts">
  import { Button } from '$lib/components/ui/button';

  let { data, onAction, stepId }: {
    data: { prompt?: string };
    onAction: (a: object) => void;
    stepId: string;
  } = $props();

  function confirm(confirmed: boolean) {
    onAction({ type: 'confirmation', step_id: stepId, confirmed });
  }
</script>

<div class="flex flex-col gap-3">
  <p class="font-medium">{data.prompt ?? 'Does this look correct?'}</p>
  <div class="flex gap-2">
    <Button onclick={() => confirm(true)}>Yes, continue →</Button>
    <Button variant="outline" onclick={() => confirm(false)}>No, redo</Button>
  </div>
</div>
