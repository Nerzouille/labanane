<svelte:options runes={true} />
<script lang="ts">
  import * as Item from "$lib/components/ui/item/index.js";
  import { HugeiconsIcon } from "@hugeicons/svelte";
  import {
    Tick02Icon, Cancel01Icon, Alert02Icon,
    CheckmarkBadge01Icon, InformationCircleIcon,
    UserIcon, FlashIcon, ChartDecreaseIcon,
  } from "@hugeicons/core-free-icons";
  import ViabilityScoreChart from "$lib/components/charts/ViabilityScoreChart.svelte";
  import type { AiAnalysisData } from "$lib/workflow-types";

  let { data }: { data: Partial<AiAnalysisData> } = $props();

  const verdict = $derived(data.go_no_go ?? 'conditional');
  const verdictIcon = $derived(
    verdict === 'go' ? Tick02Icon :
    verdict === 'no-go' ? Cancel01Icon :
    Alert02Icon
  );
  const verdictLabel = $derived(
    verdict === 'go' ? 'Go' : verdict === 'no-go' ? 'No-Go' : 'Conditional'
  );
  const verdictIconClass = $derived(
    verdict === 'go' ? 'text-green-600' :
    verdict === 'no-go' ? 'text-red-600' :
    'text-yellow-600'
  );
  const verdictItemClass = $derived(
    verdict === 'go' ? 'border-green-500/40 bg-green-500/10' :
    verdict === 'no-go' ? 'border-red-500/40 bg-red-500/10' :
    'border-yellow-500/40 bg-yellow-500/10'
  );
  const verdictTitleClass = $derived(
    verdict === 'go' ? 'text-green-700' :
    verdict === 'no-go' ? 'text-red-700' :
    'text-yellow-700'
  );
</script>

<div class="flex flex-col gap-3">

  <!-- Score chart + verdict -->
  <div class="flex items-stretch gap-3">
    {#if data.viability_score !== undefined}
      <ViabilityScoreChart score={data.viability_score} />
    {/if}
    <div class="flex-1 min-w-0">
      <Item.Root variant="outline" size="sm" class="h-full {verdictItemClass}">
        <Item.Media>
          <HugeiconsIcon icon={verdictIcon} class="s-5 {verdictIconClass}" />
        </Item.Media>
        <Item.Content>
          <Item.Title class={verdictTitleClass}>{verdictLabel}</Item.Title>
          {#if data.summary}
            <Item.Description>{data.summary}</Item.Description>
          {/if}
        </Item.Content>
      </Item.Root>
    </div>
  </div>

  <!-- Analysis text -->
  {#if data.analysis}
    <p class="text-sm text-muted-foreground leading-relaxed">{data.analysis}</p>
  {/if}

  <!-- Scoring criteria bars -->
  {#if data.criteria && data.criteria.length}
    <div class="rounded-lg border bg-card p-3 flex flex-col gap-2">
      <p class="text-xs font-medium text-muted-foreground">Scoring criteria</p>
      {#each data.criteria as c}
        {@const barColor = c.score >= 70 ? 'bg-green-500' : c.score >= 40 ? 'bg-yellow-500' : 'bg-red-500'}
        <div class="flex items-center gap-2">
          <span class="text-xs text-muted-foreground w-32 shrink-0 truncate">{c.label}</span>
          <div class="flex-1 h-1.5 rounded-full bg-muted/40">
            <div class="h-full rounded-full {barColor} transition-all" style="width: {c.score}%"></div>
          </div>
          <span class="text-xs font-medium tabular-nums w-8 text-right">{c.score}</span>
        </div>
      {/each}
    </div>
  {/if}

  <!-- Target persona -->
  {#if data.target_persona?.description}
    <Item.Root variant="default" size="sm">
      <Item.Media>
        <HugeiconsIcon icon={UserIcon} class="s-5 text-blue-500" />
      </Item.Media>
      <Item.Content>
        <Item.Title>Target persona</Item.Title>
        <Item.Description>{data.target_persona.description}</Item.Description>
      </Item.Content>
    </Item.Root>
  {/if}

  <!-- Differentiation angles -->
  {#if data.differentiation_angles?.content}
    <Item.Root variant="default" size="sm">
      <Item.Media>
        <HugeiconsIcon icon={FlashIcon} class="s-5 text-purple-500" />
      </Item.Media>
      <Item.Content>
        <Item.Title>Differentiation angles</Item.Title>
        <Item.Description>{data.differentiation_angles.content}</Item.Description>
      </Item.Content>
    </Item.Root>
  {/if}

  <!-- Competitive overview -->
  {#if data.competitive_overview?.content}
    <Item.Root variant="default" size="sm">
      <Item.Media>
        <HugeiconsIcon icon={ChartDecreaseIcon} class="s-5 text-orange-500" />
      </Item.Media>
      <Item.Content>
        <Item.Title>Competitive overview</Item.Title>
        <Item.Description>{data.competitive_overview.content}</Item.Description>
      </Item.Content>
    </Item.Root>
  {/if}

  <!-- Opportunities -->
  {#if data.key_opportunities && data.key_opportunities.length}
    {#each data.key_opportunities as o}
      <Item.Root variant="default" size="sm">
        <Item.Media>
          <HugeiconsIcon icon={CheckmarkBadge01Icon} class="s-5 text-green-600" />
        </Item.Media>
        <Item.Content>
          <Item.Title>{o}</Item.Title>
        </Item.Content>
      </Item.Root>
    {/each}
  {/if}

  <!-- Risks -->
  {#if data.key_risks && data.key_risks.length}
    {#each data.key_risks as r}
      <Item.Root variant="default" size="sm">
        <Item.Media>
          <HugeiconsIcon icon={InformationCircleIcon} class="s-5 text-destructive" />
        </Item.Media>
        <Item.Content>
          <Item.Title>{r}</Item.Title>
        </Item.Content>
      </Item.Root>
    {/each}
  {/if}

</div>
