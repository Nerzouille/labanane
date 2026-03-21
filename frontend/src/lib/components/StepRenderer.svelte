<svelte:options runes={true} />
<script lang="ts">
  import type { Component } from 'svelte';
  import StepDescriptionInput from './steps/StepDescriptionInput.svelte';
  import StepKeywordList from './steps/StepKeywordList.svelte';
  import StepConfirmation from './steps/StepConfirmation.svelte';
  import StepProductList from './steps/StepProductList.svelte';
  import StepMarketData from './steps/StepMarketData.svelte';
  import StepAnalysisStream from './steps/StepAnalysisStream.svelte';
  import StepFinalCriteria from './steps/StepFinalCriteria.svelte';
  import StepReport from './steps/StepReport.svelte';

  const COMPONENTS: Record<string, Component> = {
    product_description_input: StepDescriptionInput,
    keyword_list: StepKeywordList,
    confirmation: StepConfirmation,
    product_list: StepProductList,
    market_data_summary: StepMarketData,
    analysis_stream: StepAnalysisStream,
    final_criteria: StepFinalCriteria,
    report: StepReport,
  };

  let { componentType, data, tokens, stepId, onAction }: {
    componentType: string;
    data: Record<string, unknown>;
    tokens?: string;
    stepId: string;
    onAction: (action: object) => void;
  } = $props();

  const Comp = $derived(COMPONENTS[componentType]);
</script>

{#if Comp}
  <Comp {data} {tokens} {stepId} {onAction} />
{:else}
  <p style="color:#c00; font-size:0.85rem;">Unknown component type: {componentType}</p>
{/if}
