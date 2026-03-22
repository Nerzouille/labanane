<svelte:options runes={true} />
<script lang="ts">
  import * as Item from "$lib/components/ui/item/index.js";
  import { HugeiconsIcon } from "@hugeicons/svelte";
  import {
    UserIcon,
    ArrowLeft01Icon,
    ArrowRight01Icon,
    UserMultiple02Icon,
    HeartCheckIcon,
    AlertDiamondIcon,
  } from "@hugeicons/core-free-icons";
  import type { PersonaSetData, Persona } from "$lib/workflow-types";

  let { data }: { data: Partial<PersonaSetData> } = $props();

  const personas: Persona[] = $derived(data.personas ?? []);
  const total = $derived(personas.length);

  let activeIndex = $state(0);

  const current: Persona | undefined = $derived(personas[activeIndex]);

  function prev() {
    activeIndex = (activeIndex - 1 + total) % total;
  }

  function next() {
    activeIndex = (activeIndex + 1) % total;
  }

  function goTo(i: number) {
    activeIndex = i;
  }
</script>

{#if personas.length === 0}
  <p class="text-sm text-muted-foreground">No personas generated.</p>
{:else}
  <div class="flex flex-col gap-3">

    <!-- Header row: label + position indicator -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <HugeiconsIcon icon={UserMultiple02Icon} class="s-4 text-blue-500" />
        <span class="text-sm font-medium">Buyer Personas</span>
      </div>
      <span class="text-xs text-muted-foreground tabular-nums">{activeIndex + 1} / {total}</span>
    </div>

    <!-- Persona card -->
    {#if current}
      <div class="rounded-lg border bg-card p-4 flex flex-col gap-3">

        <!-- Name + age + occupation -->
        <div class="flex items-start gap-3">
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-blue-500/10 border border-blue-500/20">
            <HugeiconsIcon icon={UserIcon} class="s-5 text-blue-500" />
          </div>
          <div class="min-w-0">
            <p class="font-semibold leading-tight">{current.name}</p>
            <p class="text-xs text-muted-foreground mt-0.5">
              {current.age_range} · {current.occupation}
            </p>
          </div>
        </div>

        <!-- Motivations -->
        {#if current.motivations.length > 0}
          <Item.Root variant="default" size="sm">
            <Item.Media>
              <HugeiconsIcon icon={HeartCheckIcon} class="s-5 text-green-500" />
            </Item.Media>
            <Item.Content>
              <Item.Title>Motivations</Item.Title>
              <Item.Description>
                <ul class="mt-0.5 flex flex-col gap-0.5">
                  {#each current.motivations as m}
                    <li class="before:content-['·'] before:mr-1.5 before:text-muted-foreground">{m}</li>
                  {/each}
                </ul>
              </Item.Description>
            </Item.Content>
          </Item.Root>
        {/if}

        <!-- Pain points -->
        {#if current.pain_points.length > 0}
          <Item.Root variant="default" size="sm">
            <Item.Media>
              <HugeiconsIcon icon={AlertDiamondIcon} class="s-5 text-red-500" />
            </Item.Media>
            <Item.Content>
              <Item.Title>Pain points</Item.Title>
              <Item.Description>
                <ul class="mt-0.5 flex flex-col gap-0.5">
                  {#each current.pain_points as p}
                    <li class="before:content-['·'] before:mr-1.5 before:text-muted-foreground">{p}</li>
                  {/each}
                </ul>
              </Item.Description>
            </Item.Content>
          </Item.Root>
        {/if}

      </div>
    {/if}

    <!-- Dot navigator + prev/next buttons -->
    <div class="flex items-center justify-between">

      <button
        onclick={prev}
        class="flex items-center gap-1 rounded-md px-2 py-1 text-xs text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
        aria-label="Previous persona"
      >
        <HugeiconsIcon icon={ArrowLeft01Icon} class="s-3.5" />
        Prev
      </button>

      <!-- Dot indicators -->
      <div class="flex items-center gap-1.5">
        {#each personas as _, i}
          <button
            onclick={() => goTo(i)}
            aria-label="Go to persona {i + 1}"
            class="h-2 rounded-full transition-all duration-200 {i === activeIndex
              ? 'w-5 bg-blue-500'
              : 'w-2 bg-muted-foreground/30 hover:bg-muted-foreground/60'}"
          ></button>
        {/each}
      </div>

      <button
        onclick={next}
        class="flex items-center gap-1 rounded-md px-2 py-1 text-xs text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
        aria-label="Next persona"
      >
        Next
        <HugeiconsIcon icon={ArrowRight01Icon} class="s-3.5" />
      </button>

    </div>

  </div>
{/if}
