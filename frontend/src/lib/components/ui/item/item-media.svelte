<script lang="ts">
  let { children, class: className = '' } = $props<{ children?: any; class?: string }>();
</script>
<div class="shrink-0 {className}">{@render children?.()}</div>
