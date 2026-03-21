<script lang="ts">
  let { variant = 'default', size = 'md', class: className = '', children, ...rest } = $props<{
    variant?: 'default' | 'outline';
    size?: 'sm' | 'md';
    class?: string;
    children?: any;
    [key: string]: any;
  }>();
</script>

<div
  class="flex items-start gap-3 rounded-lg border p-3
    {size === 'sm' ? 'p-2.5 text-sm' : 'p-3'}
    {variant === 'outline' ? 'border-border bg-transparent' : 'border-transparent bg-muted/40'}
    {className}"
  {...rest}
>
  {@render children?.()}
</div>
