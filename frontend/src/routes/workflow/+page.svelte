<svelte:options runes={true} />
<script lang="ts">
  import { createWorkflowConnection, type WorkflowConnection } from '$lib/ws';
  import StepRenderer from '$lib/components/StepRenderer.svelte';
  import StepSkeleton from '$lib/components/steps/StepSkeleton.svelte';
  import type { StepState, WsStatus } from '$lib/workflow-types';
  import { Alert, AlertDescription } from '$lib/components/ui/alert';
  import { Spinner } from '$lib/components/ui/spinner';
  import ShaderBackground from '$lib/components/ShaderBackground.svelte';
  import { HugeiconsIcon } from '@hugeicons/svelte';
  import { ArrowRightIcon } from '@hugeicons/core-free-icons';
  import { fly, slide } from 'svelte/transition';
  import { tick } from 'svelte';

  const WS_URL = 'ws://localhost:8000/ws/workflow';

  let workflowState = $state({
    status: 'idle' as WsStatus,
    description: '',
    totalSteps: 0,
    steps: [] as StepState[],
    activeStepId: '',
    errorMsg: '',
    runId: '',
  });

  let conn: WorkflowConnection | null = null;
  let intentionalClose = false;
  let loopBackStepId = $state('');   // set when engine loops back to a user_input step
  const isIdle = $derived(workflowState.status === 'idle' || loopBackStepId !== '');

  const HIDDEN_STEPS = new Set(['product_description', 'ai_analysis']);
  const visibleSteps = $derived(
    workflowState.steps.filter((s) => !HIDDEN_STEPS.has(s.step_id))
  );

  // ── Blend : 0 = dark shader, 1 = vague élargie = blanc ──────────────────
  let shaderBlend = $state(0);
  $effect(() => {
    const target = isIdle ? 0 : 1;
    const start = performance.now();
    const from = shaderBlend;
    let raf: number;
    function tick(now: number) {
      const t = Math.min((now - start) / 80, 1);
      const e = t < 0.5 ? 2*t*t : -1+(4-2*t)*t;
      shaderBlend = from + (target - from) * e;
      if (t < 1) raf = requestAnimationFrame(tick);
    }
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  });

  // Auto-scroll to new content when near the bottom (chat-like behaviour).
  // Track length, status, data AND tokens so product batches and streaming also trigger scroll.
  $effect(() => {
    const _len = visibleSteps.length;
    const last = visibleSteps.at(-1);
    const _status = last?.status;
    const _data = last?.data;
    const _tokens = last?.tokens;
    tick().then(() => {
      const nearBottom = window.innerHeight + window.scrollY >= document.body.scrollHeight - 100;
      if (nearBottom) {
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
      }
    });
  });

  function findOrCreateStep(step_id: string): StepState {
    let s = workflowState.steps.find((s) => s.step_id === step_id);
    if (!s) {
      s = { step_id, step_number: 0, label: step_id, status: 'pending' };
      workflowState.steps = [...workflowState.steps, s];
    }
    return s;
  }

  function updateStep(step_id: string, patch: Partial<StepState>) {
    workflowState.steps = workflowState.steps.map((s) =>
      s.step_id === step_id ? { ...s, ...patch } : s,
    );
  }

  function startWorkflow(e: SubmitEvent) {
    e.preventDefault();
    if (!workflowState.description.trim()) return;

    // Loop-back: connection is still open, just send user_input
    if (loopBackStepId) {
      conn?.send({ type: 'user_input', step_id: loopBackStepId, data: { description: workflowState.description } });
      loopBackStepId = '';
      return;
    }

    workflowState.steps = [];
    workflowState.errorMsg = '';
    workflowState.runId = '';
    intentionalClose = false;

    conn = createWorkflowConnection(WS_URL, {
      onStatusChange(status) {
        workflowState.status = status;
        if (status === 'closed' && !intentionalClose) {
          workflowState.errorMsg = 'Connection lost — please start a new analysis.';
        }
      },
      onError(err) { workflowState.errorMsg = err; },
      onMessage(msg) {
        if (msg.type === 'workflow_started') {
          workflowState.totalSteps = msg.total_steps;
        } else if (msg.type === 'step_activated') {
          const existing = workflowState.steps.find(s => s.step_id === msg.step_id);
          if (existing && existing.status === 'complete') {
            // Loop-back: step was already completed, engine is re-running it
            loopBackStepId = msg.step_id;
            // Remove steps that came after this step (they're being re-done)
            const idx = workflowState.steps.findIndex(s => s.step_id === msg.step_id);
            workflowState.steps = workflowState.steps.slice(0, idx);
          }
          findOrCreateStep(msg.step_id);
          updateStep(msg.step_id, { step_number: msg.step_number, label: msg.label, status: 'active' });
          workflowState.activeStepId = msg.step_id;
        } else if (msg.type === 'step_processing') {
          updateStep(msg.step_id, { status: 'processing' });
        } else if (msg.type === 'step_streaming_token') {
          workflowState.steps = workflowState.steps.map((s) =>
            s.step_id === msg.step_id
              ? { ...s, tokens: (s.tokens ?? '') + msg.token, status: 'processing' }
              : s,
          );
        } else if (msg.type === 'step_result') {
          updateStep(msg.step_id, {
            status: 'complete',
            component_type: msg.component_type,
            data: msg.data as Record<string, unknown>,
          });
        } else if (msg.type === 'confirmation_request') {
          updateStep(msg.step_id, {
            status: 'confirmation',
            component_type: msg.component_type,
            data: msg.data as Record<string, unknown>,
          });
        } else if (msg.type === 'step_error') {
          updateStep(msg.step_id, { status: 'error', error: msg.error, data: { retryable: msg.retryable } });
          if (!msg.retryable) workflowState.errorMsg = msg.error;
        } else if (msg.type === 'workflow_complete') {
          intentionalClose = true;
          workflowState.runId = msg.run_id;
          workflowState.status = 'closed';
        }
      },
    });

    conn.send({ type: 'start', description: workflowState.description });
  }

  function handleStepAction(action: object) {
    conn?.send(action);
    const a = action as { type: string; step_id?: string; confirmed?: boolean };
    if (a.type === 'confirmation' && a.step_id) {
      if (a.confirmed === false) {
        reset();
      } else {
        updateStep(a.step_id, { status: 'complete' });
      }
    }
  }

  function reset() {
    intentionalClose = true;
    loopBackStepId = '';
    conn?.close();
    conn = null;
    workflowState = { status: 'idle', description: '', totalSteps: 0, steps: [], activeStepId: '', errorMsg: '', runId: '' };
  }

  $effect(() => () => conn?.close());
</script>

<ShaderBackground blend={shaderBlend} />

<div class="theme" class:dark={isIdle}>

  <!-- Logo top-left -->
  <div class="logo-topleft" class:visible={!isIdle}>Shipper</div>

  <!-- Wrapper centré : barre + hero -->
  <div class="float-wrapper" class:compact={!isIdle}>

    <div class="hero-text" class:hidden={!isIdle}>
      <h1 class="brand">Shipper</h1>
      <p class="tagline">Analysez votre marché en temps réel</p>
    </div>

    <form onsubmit={startWorkflow} class="search-form">
      <div class="search-bar">
        <input
          type="text"
          bind:value={workflowState.description}
          placeholder="Décrivez un produit ou entrez un mot-clé…"
          disabled={!isIdle}
          autocomplete="off"
          spellcheck="false"
        />
        {#if isIdle}
          <button type="submit" disabled={!workflowState.description.trim()}>
            <span class="btn-label">Analyser</span>
            <span class="btn-icon"><HugeiconsIcon icon={ArrowRightIcon} size={18} color="currentColor" /></span>
          </button>
        {:else}
          <button type="button" class="reset-btn" onclick={reset}>Nouvelle analyse</button>
        {/if}
      </div>
    </form>

    <div class="chips" class:hidden={!isIdle}>
      {#each ['Vélo électrique', 'Cosmétiques bio', 'Drone FPV'] as chip}
        <button class="chip" type="button" onclick={() => { workflowState.description = chip; }}>
          {chip}
        </button>
      {/each}
    </div>
  </div>

  <!-- Steps -->
  {#if !isIdle}
    <main in:fly={{ y: 28, duration: 600, delay: 700 }}>

      {#if workflowState.errorMsg}
        <Alert variant="destructive" class="mb-6">
          <AlertDescription>{workflowState.errorMsg}</AlertDescription>
        </Alert>
      {/if}

      <div class="steps-list">
        {#each visibleSteps as step (step.step_id)}
          <div out:slide={{ axis: 'y', duration: 350 }}>
            {#if (step.status === 'active' || step.status === 'processing') && !step.component_type}
              <div in:fly={{ y: 10, duration: 300 }}>
                <StepSkeleton stepId={step.step_id} />
              </div>
            {:else if step.component_type && step.status !== 'error'}
              <div in:fly={{ y: 10, duration: 300 }}>
                <StepRenderer
                  componentType={step.component_type}
                  data={step.data ?? {}}
                  tokens={step.tokens}
                  stepId={step.step_id}
                  status={step.status}
                  onAction={handleStepAction}
                />
              </div>
            {:else if step.status === 'error'}
              <div class="step-error-row" in:fly={{ y: 10, duration: 300 }}>
                <p class="step-error-msg">{step.error}</p>
                {#if step.data?.retryable}
                  <button class="retry-btn" onclick={() => handleStepAction({ type: 'retry', step_id: step.step_id })}>
                    Retry
                  </button>
                {/if}
              </div>
            {/if}
          </div>
        {/each}
      </div>

      {#if workflowState.runId}
        <div class="complete-bar">
          <p class="complete-text">Analyse terminée</p>
          <button class="reset-btn-bottom" onclick={reset}>Nouvelle analyse</button>
        </div>
      {:else if workflowState.errorMsg}
        <div class="mt-6 flex justify-end">
          <button class="reset-btn-bottom" onclick={reset}>Nouvelle analyse</button>
        </div>
      {:else if workflowState.status === 'open' && visibleSteps.at(-1)?.status === 'complete'}
        <div class="flex justify-center py-6" in:fly={{ y: 6, duration: 200 }}>
          <Spinner class="size-5 text-muted-foreground" />
        </div>
      {/if}

    </main>
  {/if}

</div>

<style>
  :global(body) {
    margin: 0; padding: 0;
    background: #f7f7fc;
    font-family: system-ui, -apple-system, sans-serif;
  }

  :root { --theme-dur: 0.5s; }

  /* ── Wrapper thème ── */
  .theme { color: #1e293b; }
  .theme.dark { color: #e2e8f0; }

  /* ── Logo top-left ── */
  .logo-topleft {
    position: fixed;
    top: 1.5rem;
    left: 2rem;
    z-index: 20;
    font-size: 1.2rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    opacity: 0;
    pointer-events: none;
    color: #3b82f6;
    transition: opacity 0.6s ease 0.5s, color var(--theme-dur) ease;
  }
  .logo-topleft.visible { opacity: 1; pointer-events: auto; }
  .dark .logo-topleft { color: #fff; }


  /* ── Float wrapper ── */
  .float-wrapper {
    position: fixed;
    z-index: 10;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: min(720px, calc(100% - 4rem));
    display: flex;
    flex-direction: column;
    align-items: center;
    transition:
      top 0.95s cubic-bezier(0.4, 0, 0.2, 1),
      transform 0.95s cubic-bezier(0.4, 0, 0.2, 1);
  }
  .float-wrapper.compact {
    top: 1.5rem;
    transform: translateX(-50%);
  }

  /* ── Hero text ── */
  .hero-text {
    display: flex;
    flex-direction: column;
    align-items: center;
    overflow: hidden;
    max-height: 14rem;
    opacity: 1;
    transition:
      max-height 0.8s cubic-bezier(0.4, 0, 0.2, 1),
      opacity 0.4s ease,
      margin 0.8s ease;
    margin-bottom: 0.35rem;
  }
  .hero-text.hidden { max-height: 0; opacity: 0; margin-bottom: 0; }

  .brand {
    font-size: clamp(3rem, 8vw, 5rem);
    font-weight: 700;
    color: #1e293b;
    letter-spacing: -0.04em;
    margin: 0 0 0.25rem;
    line-height: 1;
    transition: color var(--theme-dur) ease;
  }
  .dark .brand { color: #fff; }

  .tagline {
    color: #64748b;
    font-size: 1rem;
    margin: 0 0 1.75rem;
    transition: color var(--theme-dur) ease;
  }
  .dark .tagline { color: #94a3b8; }

  /* ── Search form ── */
  .search-form { width: 100%; margin-bottom: 1rem; }

  .search-bar {
    display: flex;
    align-items: center;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(8px);
    border: 1px solid #cbd5e1;
    border-radius: 14px;
    padding: 0.35rem 0.35rem 0.35rem 1.25rem;
    transition: border-color 0.2s, background var(--theme-dur) ease;
  }
  .search-bar:focus-within { border-color: #3b82f6; }
  .dark .search-bar { background: rgba(15, 23, 42, 0.85); border-color: #334155; }
  .dark .search-bar:focus-within { border-color: #7c3aed; }

  input {
    flex: 1;
    background: transparent;
    border: none;
    padding: 0.65rem 0;
    font-size: 1.05rem;
    color: #1e293b;
    outline: none;
    min-width: 0;
    transition: color var(--theme-dur) ease;
  }
  .dark input { color: #fff; }
  input::placeholder { color: #94a3b8; }
  .dark input::placeholder { color: #475569; }
  input:disabled { cursor: default; }

  button[type='submit'] {
    background: #3b82f6;
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 0.65rem 1.4rem;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    white-space: nowrap;
    flex-shrink: 0;
    transition: background 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .btn-icon { display: none; align-items: center; justify-content: center; }
  button[type='submit']:disabled { opacity: 0.4; cursor: not-allowed; }
  button[type='submit']:not(:disabled):hover { background: #2563eb; }
  .dark button[type='submit'] { background: #7c3aed; }
  .dark button[type='submit']:not(:disabled):hover { background: #6d28d9; }

  .reset-btn {
    background: transparent;
    color: #64748b;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 0.45rem 0.9rem;
    font-size: 0.8rem;
    cursor: pointer;
    white-space: nowrap;
    flex-shrink: 0;
    transition: color 0.15s, border-color 0.15s;
  }
  .reset-btn:hover { color: #1e293b; border-color: #3b82f6; }
  .dark .reset-btn { border-color: #334155; }
  .dark .reset-btn:hover { color: #e2e8f0; border-color: #7c3aed; }

  /* ── Chips ── */
  .chips {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    justify-content: center;
    overflow: hidden;
    max-height: 8rem;
    opacity: 1;
    transition: max-height 0.7s ease, opacity 0.35s ease, margin 0.7s ease;
    margin-top: 0;
    padding: 0 0.25rem;
  }
  .chips.hidden { max-height: 0; opacity: 0; }

  .chip {
    background: rgba(0,0,0,0.04);
    border: 1px solid rgba(0,0,0,0.1);
    color: #475569;
    border-radius: 999px;
    padding: 0.35rem 0.9rem;
    font-size: 0.8rem;
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s, color 0.15s;
  }
  .chip:hover { background: rgba(59,130,246,0.12); border-color: #3b82f6; color: #1e40af; }
  .dark .chip { background: rgba(255,255,255,0.06); border-color: rgba(255,255,255,0.12); color: #cbd5e1; }
  .dark .chip:hover { background: rgba(124,58,237,0.2); border-color: #7c3aed; color: #fff; }

  /* ── Steps main ── */
  main {
    position: relative;
    z-index: 1;
    width: min(720px, calc(100% - 4rem));
    margin: 0 auto;
    padding: 7rem 0 4rem;
  }

  .steps-list { display: flex; flex-direction: column; gap: 2rem; }

  .step-error-row { display: flex; align-items: center; gap: 0.75rem; }
  .step-error-msg { font-size: 0.85rem; color: #ef4444; margin: 0; }
  .retry-btn {
    font-size: 0.8rem;
    padding: 0.3rem 0.75rem;
    border: 1px solid #ef4444;
    border-radius: 6px;
    color: #ef4444;
    background: transparent;
    cursor: pointer;
    white-space: nowrap;
    flex-shrink: 0;
    transition: background 0.15s, color 0.15s;
  }
  .retry-btn:hover { background: #ef4444; color: #fff; }

  /* ── Complete bar ── */
  .complete-bar {
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid #e2e8f0;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .complete-text { font-size: 0.875rem; color: #64748b; }
  .reset-btn-bottom {
    background: #3b82f6;
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 0.55rem 1.2rem;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }
  .reset-btn-bottom:hover { background: #2563eb; }

  /* ── Mobile overrides (en dernier pour l'emporter sur les règles de base) ── */
  @media (max-width: 640px) {
    .logo-topleft { display: none; }
    .btn-label { display: none; }
    .btn-icon { display: flex; }
    button[type='submit'] { padding: 0.65rem 0.75rem; }
    input { font-size: 0.85rem; }
  }
</style>
