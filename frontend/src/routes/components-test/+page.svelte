<svelte:options runes={true} />
<script lang="ts">
  import StepRenderer from '$lib/components/StepRenderer.svelte';
  import { Card, CardHeader, CardTitle, CardContent } from '$lib/components/ui/card';
  import { Badge } from '$lib/components/ui/badge';
  import { Alert, AlertDescription } from '$lib/components/ui/alert';
  import { Separator } from '$lib/components/ui/separator';

  const fixtures = [
    {
      title: 'StepDescriptionInput',
      componentType: 'product_description_input',
      stepId: 'product_description',
      data: { text: 'ergonomic desk mats for remote workers' },
    },
    {
      title: 'StepKeywordList',
      componentType: 'keyword_list',
      stepId: 'keyword_refinement',
      data: { keywords: ['ergonomic desk mat', 'office accessories', 'wrist rest pad', 'desk setup'] },
    },
    {
      title: 'StepConfirmation',
      componentType: 'confirmation',
      stepId: 'keyword_confirmation',
      data: { prompt: 'Do these keywords look correct for your product idea?' },
    },
    {
      title: 'StepProductList',
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
    {
      title: 'StepMarketData',
      componentType: 'market_data_summary',
      stepId: 'market_research',
      data: {
        sources_available: ['amazon', 'google_trends'],
        sources_unavailable: ['reddit'],
        trend_summary: 'Search volume for "ergonomic desk mat" has grown 24% YoY, with peaks in January and September.',
        sentiment_summary: 'Community discussions highlight comfort and durability as primary purchase drivers.',
      },
    },
    {
      title: 'StepAnalysisStream — Streaming',
      componentType: 'analysis_stream',
      stepId: 'ai_analysis',
      data: { complete: false, content: '' },
      tokens: 'The ergonomic desk mat market shows moderate competition with strong growth potential…',
    },
    {
      title: 'StepAnalysisStream — Complete',
      componentType: 'analysis_stream',
      stepId: 'ai_analysis_done',
      data: {
        complete: true,
        content: 'The market shows 42/100 viability. Key differentiators: eco-friendly materials and customizable sizing. Primary risk: high competition from established brands.',
      },
    },
    {
      title: 'StepFinalCriteria — Go',
      componentType: 'final_criteria',
      stepId: 'final_criteria_go',
      data: {
        summary: 'The product shows solid market potential with identifiable differentiation angles.',
        go_no_go: 'go',
        key_risks: ['High competition from Amazon brands', 'Price sensitivity in mid-market'],
        key_opportunities: ['Eco-friendly niche underserved', 'B2B office supply channel', 'Subscription model for replacements'],
      },
    },
    {
      title: 'StepFinalCriteria — No-Go',
      componentType: 'final_criteria',
      stepId: 'final_criteria_nogo',
      data: {
        summary: 'Market is saturated with low-cost alternatives and low differentiation potential.',
        go_no_go: 'no-go',
        key_risks: ['Margin compression from Asian suppliers', 'Brand recognition barrier', 'High customer acquisition cost'],
        key_opportunities: ['Premium segment niche (small TAM)'],
      },
    },
    {
      title: 'StepFinalCriteria — Conditional',
      componentType: 'final_criteria',
      stepId: 'final_criteria_cond',
      data: {
        summary: 'Viable if product differentiates on eco-certification and targets B2B.',
        go_no_go: 'conditional',
        key_risks: ['Eco-certification cost', 'B2B sales cycle length'],
        key_opportunities: ['Corporate sustainability mandates', 'Government procurement'],
      },
    },
    {
      title: 'StepReport',
      componentType: 'report',
      stepId: 'report_generation',
      data: {
        run_id: 'abc123-fake-run-id',
        markdown_available: false,
        note: 'Report stub — export will be available once business logic is implemented.',
      },
    },
  ];

  let actions = $state<string[]>([]);

  function handleAction(label: string, action: object) {
    actions = [`[${label}] ${JSON.stringify(action)}`, ...actions.slice(0, 9)];
  }
</script>

<main class="max-w-4xl mx-auto py-8 px-4">
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

  <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
    {#each fixtures as f}
      <Card>
        <CardHeader class="pb-2">
          <div class="flex items-center justify-between gap-2">
            <CardTitle class="text-sm font-semibold">{f.title}</CardTitle>
            <Badge variant="secondary" class="text-xs font-mono">{f.componentType}</Badge>
          </div>
        </CardHeader>
        <Separator />
        <CardContent class="pt-3">
          <StepRenderer
            componentType={f.componentType}
            data={f.data}
            tokens={f.tokens}
            stepId={f.stepId}
            onAction={(a) => handleAction(f.title, a)}
          />
        </CardContent>
      </Card>
    {/each}
  </div>
</main>
