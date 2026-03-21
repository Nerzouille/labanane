<svelte:options runes={true} />
<script lang="ts">
  import { Button } from '$lib/components/ui/button';
  import { HugeiconsIcon } from '@hugeicons/svelte';
  import { ArrowRight01Icon, Cancel01Icon } from '@hugeicons/core-free-icons';

  let { data, onAction, stepId }: {
    data: { prompt?: string };
    onAction: (a: object) => void;
    stepId: string;
  } = $props();

  function confirm(confirmed: boolean) {
    onAction({ type: 'confirmation', step_id: stepId, confirmed });
  }
</script>

<div class="flex flex-col gap-3 items-center">
  <p class="font-medium">{data.prompt ?? 'Does this look correct?'}</p>
  <div class="flex items-center gap-3">
    <button
      class="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
      onclick={() => confirm(false)}
    >
      <HugeiconsIcon icon={Cancel01Icon} size={15} />
      No, redo
    </button>
    <Button onclick={() => confirm(true)} class="flex items-center gap-1.5">
      Yes, continue
      <HugeiconsIcon icon={ArrowRight01Icon} size={16} />
    </Button>
  </div>
</div>
