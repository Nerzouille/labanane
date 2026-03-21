<script lang="ts">
  let { children, class: className = '' } = $props<{ children?: any; class?: string }>();
</script>
<p class="text-sm text-muted-foreground {className}">{@render children?.()}</p>
