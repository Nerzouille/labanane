<script lang="ts">
  let { children, class: className = '' } = $props<{ children?: any; class?: string }>();
</script>
<div class="flex flex-col gap-0.5 min-w-0 {className}">{@render children?.()}</div>
