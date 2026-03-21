<svelte:options runes={true} />
<script lang="ts">
  import StepRenderer from '$lib/components/StepRenderer.svelte';
  import { Card, CardHeader, CardTitle, CardContent } from '$lib/components/ui/card';
  import { Badge } from '$lib/components/ui/badge';
  import { Alert, AlertDescription } from '$lib/components/ui/alert';
  import { Separator } from '$lib/components/ui/separator';
  import { Tabs, TabsList, TabsTrigger, TabsContent } from '$lib/components/ui/tabs';

  type Fixture = {
    label: string;
    componentType: string;
    stepId: string;
    data: Record<string, unknown>;
    tokens?: string;
  };

  type ComponentGroup = {
    title: string;
    componentType: string;
    variants: Fixture[];
  };

  const groups: ComponentGroup[] = [
    {
      title: 'StepKeywordList',
      componentType: 'keyword_list',
      variants: [
        {
          label: 'Default',
          componentType: 'keyword_list',
          stepId: 'keyword_refinement',
          data: { keywords: ['ergonomic desk mat', 'office accessories', 'wrist rest pad', 'desk setup'] },
        },
      ],
    },
    {
      title: 'StepConfirmation',
      componentType: 'confirmation',
      variants: [
        {
          label: 'Default',
          componentType: 'confirmation',
          stepId: 'keyword_confirmation',
          data: { prompt: 'Do these keywords look correct for your product idea?' },
        },
      ],
    },
    {
      title: 'StepProductList',
      componentType: 'product_list',
      variants: [
        {
          label: 'Default',
          componentType: 'product_list',
          stepId: 'product_research',
          data: {
            products: [
              { title: 'ProDesk Anti-Fatigue Mat', price: '$34.99', url: 'https://example.com/1' },
              { title: 'ErgoMat Premium Desk Pad', price: '$49.99', url: 'https://example.com/2' },
              { title: 'ComfortPlus Office Mat', price: '$27.99', url: 'https://example.com/3' },
            ],
          },
        },
      ],
    },
    {
      title: 'StepMarketData',
      componentType: 'market_data_summary',
      variants: [
        {
          label: 'Default',
          componentType: 'market_data_summary',
          stepId: 'market_research',
          data: {
            sources_available: ['amazon', 'google_trends'],
            sources_unavailable: ['reddit'],
            trend_summary: 'Search volume for "ergonomic desk mat" has grown 24% YoY, with peaks in January and September.',
            sentiment_summary: 'Community discussions highlight comfort and durability as primary purchase drivers.',
          },
        },
      ],
    },
    {
      title: 'StepFinalCriteria',
      componentType: 'final_criteria',
      variants: [
        {
          label: 'Go',
          componentType: 'final_criteria',
          stepId: 'final_criteria_go',
          data: {
            go_no_go: 'go',
            viability_score: 74,
            summary: 'The product shows solid market potential with identifiable differentiation angles.',
            analysis: 'The ergonomic desk mat market shows moderate competition with strong growth potential. Eco-friendly materials and customizable sizing represent underserved differentiation angles. Search volume has grown 24% YoY with sustained demand signals.',
            criteria: [
              { label: 'Market size', score: 80 },
              { label: 'Competition', score: 62 },
              { label: 'Differentiation', score: 78 },
              { label: 'Margin potential', score: 71 },
              { label: 'Time to market', score: 65 },
            ],
            key_opportunities: ['Eco-friendly niche underserved', 'B2B office supply channel', 'Subscription model for replacements'],
            key_risks: ['High competition from Amazon brands', 'Price sensitivity in mid-market'],
          },
        },
        {
          label: 'No-Go',
          componentType: 'final_criteria',
          stepId: 'final_criteria_nogo',
          data: {
            go_no_go: 'no-go',
            viability_score: 28,
            summary: 'Market is saturated with low-cost alternatives and low differentiation potential.',
            analysis: 'The market is dominated by established brands with entrenched supply chains. Margins are heavily compressed by Asian manufacturers. Customer acquisition costs make unit economics unfeasible at realistic AOVs.',
            criteria: [
              { label: 'Market size', score: 55 },
              { label: 'Competition', score: 18 },
              { label: 'Differentiation', score: 22 },
              { label: 'Margin potential', score: 25 },
              { label: 'Time to market', score: 40 },
            ],
            key_opportunities: ['Premium segment niche (small TAM)'],
            key_risks: ['Margin compression from Asian suppliers', 'Brand recognition barrier', 'High customer acquisition cost'],
          },
        },
        {
          label: 'Conditional',
          componentType: 'final_criteria',
          stepId: 'final_criteria_cond',
          data: {
            go_no_go: 'conditional',
            viability_score: 51,
            summary: 'Viable if product differentiates on eco-certification and targets B2B.',
            analysis: 'The opportunity exists but requires a focused go-to-market. B2B procurement cycles and sustainability mandates create a defensible wedge, provided the eco-certification cost is absorbed in the first 12 months.',
            criteria: [
              { label: 'Market size', score: 60 },
              { label: 'Competition', score: 45 },
              { label: 'Differentiation', score: 58 },
              { label: 'Margin potential', score: 50 },
              { label: 'Time to market', score: 42 },
            ],
            key_opportunities: ['Corporate sustainability mandates', 'Government procurement'],
            key_risks: ['Eco-certification cost', 'B2B sales cycle length'],
          },
        },
      ],
    },
    {
      title: 'StepReport',
      componentType: 'report',
      variants: [
        {
          label: 'Available',
          componentType: 'report',
          stepId: 'report_generation',
          data: {
            run_id: 'abc123-fake-run-id',
            markdown_available: true,
          },
        },
        {
          label: 'Failed',
          componentType: 'report',
          stepId: 'report_generation_failed',
          data: {
            markdown_available: false,
          },
        },
      ],
    },
  ];

  let actions = $state<string[]>([]);
  let refreshKeys = $state<Record<string, number>>({});

  function handleAction(title: string, action: Record<string, unknown>) {
    actions = [`[${title}] ${JSON.stringify(action)}`, ...actions.slice(0, 9)];
  }

  function refreshGroup(componentType: string) {
    refreshKeys = { ...refreshKeys, [componentType]: (refreshKeys[componentType] ?? 0) + 1 };
  }
</script>

<main class="max-w-2xl mx-auto py-8 px-4">
  <header class="flex justify-between items-center mb-2">
    <h1 class="text-xl font-bold">Component Test Page</h1>
    <a href="/" class="text-sm text-primary hover:underline">← Home</a>
  </header>
  <p class="text-muted-foreground text-sm mb-6">All workflow step components with fake data. Use this page to verify component rendering before connecting to the WebSocket backend.</p>

  {#if actions.length > 0}
    <Alert class="mb-6">
      <AlertDescription>
        <p class="font-semibold mb-2 text-xs uppercase tracking-wide">Action Log (last 10)</p>
        <div class="flex flex-col gap-1">
          {#each actions as a}
            <code class="text-xs">{a}</code>
          {/each}
        </div>
      </AlertDescription>
    </Alert>
  {/if}

  <div class="flex flex-col gap-4">
    {#each groups as group}
      {@const hasVariants = group.variants.length > 1}
      <Card>
        <CardHeader class="pb-2">
          <div class="flex items-center justify-between gap-2">
            <CardTitle class="text-sm font-semibold">{group.title}</CardTitle>
            <div class="flex items-center gap-2">
              <Badge variant="secondary" class="text-xs font-mono">{group.componentType}</Badge>
              <button
                class="text-muted-foreground hover:text-foreground transition-colors text-sm leading-none"
                title="Refresh"
                onclick={() => refreshGroup(group.componentType)}
              >↺</button>
            </div>
          </div>
        </CardHeader>
        <Separator />
        {#if hasVariants}
          <Tabs value={group.variants[0].label}>
            <div class="px-6 pt-3">
              <TabsList>
                {#each group.variants as variant}
                  <TabsTrigger value={variant.label}>{variant.label}</TabsTrigger>
                {/each}
              </TabsList>
            </div>
            {#each group.variants as variant}
              <TabsContent value={variant.label}>
                <CardContent class="pt-3">
                  {#key refreshKeys[group.componentType] ?? 0}
                    <StepRenderer
                      componentType={variant.componentType}
                      data={variant.data}
                      tokens={variant.tokens}
                      stepId={variant.stepId}
                      onAction={(a) => handleAction(group.title, a)}
                    />
                  {/key}
                </CardContent>
              </TabsContent>
            {/each}
          </Tabs>
        {:else}
          <CardContent class="pt-3">
            {#key refreshKeys[group.componentType] ?? 0}
              <StepRenderer
                componentType={group.variants[0].componentType}
                data={group.variants[0].data}
                tokens={group.variants[0].tokens}
                stepId={group.variants[0].stepId}
                onAction={(a) => handleAction(group.title, a)}
              />
            {/key}
          </CardContent>
        {/if}
      </Card>
    {/each}
  </div>
</main>
