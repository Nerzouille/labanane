<script lang="ts">
  let { children, class: className = '' } = $props<{ children?: any; class?: string }>();
</script>
<p class="font-medium leading-none {className}">{@render children?.()}</p>
