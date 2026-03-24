<script lang="ts">
  import { Card, CardHeader, CardTitle, CardDescription } from '$lib/components/ui/card';
  import { Badge } from '$lib/components/ui/badge';
</script>

<main class="max-w-lg mx-auto mt-12 px-4">
  <h1 class="text-2xl font-bold mb-1">Guided Analysis Workflow</h1>
  <p class="text-muted-foreground mb-8">9-step market intelligence analysis with keyword refinement and product validation.</p>

  <nav class="flex flex-col gap-3">
    <a href="/workflow" class="block no-underline">
      <Card class="hover:border-primary transition-colors cursor-pointer">
        <CardHeader class="pb-2">
          <div class="flex items-center justify-between">
            <CardTitle class="text-base">Start Analysis</CardTitle>
            <Badge variant="default">Active</Badge>
          </div>
          <CardDescription>9-step guided analysis with keyword refinement and product validation.</CardDescription>
        </CardHeader>
      </Card>
    </a>

    <a href="/components-test" class="block no-underline">
      <Card class="hover:border-primary transition-colors cursor-pointer">
        <CardHeader class="pb-2">
          <div class="flex items-center justify-between">
            <CardTitle class="text-base">Component Test Page</CardTitle>
            <Badge variant="outline">Dev</Badge>
          </div>
          <CardDescription>Visual test of all workflow step components with fake data.</CardDescription>
        </CardHeader>
      </Card>
    </a>
  </nav>
</main>
