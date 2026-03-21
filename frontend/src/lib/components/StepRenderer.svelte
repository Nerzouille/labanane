<svelte:options runes={true} />
<script lang="ts">
  import type { Component } from 'svelte';
  import StepKeywordList from './steps/StepKeywordList.svelte';
  import StepConfirmation from './steps/StepConfirmation.svelte';
  import StepProductList from './steps/StepProductList.svelte';
  import StepMarketData from './steps/StepMarketData.svelte';
  import StepFinalCriteria from './steps/StepFinalCriteria.svelte';
  import StepReport from './steps/StepReport.svelte';

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const COMPONENTS: Record<string, Component<any>> = {
    keyword_list: StepKeywordList,
    confirmation: StepConfirmation,
    product_list: StepProductList,
    market_data_summary: StepMarketData,
    analysis_stream: StepFinalCriteria,
    final_criteria: StepFinalCriteria,
    report: StepReport,
  };

  let { componentType, data, tokens, stepId, status, onAction }: {
    componentType: string;
    data: Record<string, unknown>;
    tokens?: string;
    stepId: string;
    status?: string;
    onAction: (action: Record<string, unknown>) => void;
  } = $props();

  const Comp = $derived(COMPONENTS[componentType]);
</script>

{#if Comp}
  <Comp {data} {tokens} {stepId} {status} {onAction} />
{:else}
  <p style="color:#c00; font-size:0.85rem;">Unknown component type: {componentType}</p>
{/if}
