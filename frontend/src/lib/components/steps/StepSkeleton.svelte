<svelte:options runes={true} />
<script lang="ts">
  import { Spinner } from '$lib/components/ui/spinner';

  let { stepId }: { stepId: string } = $props();
  void stepId; // prop kept for call-site compatibility
</script>

<div class="flex justify-center py-4">
  <Spinner class="size-5 text-muted-foreground" />
</div>
