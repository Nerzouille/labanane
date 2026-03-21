<svelte:options runes={true} />
<script lang="ts">
  import { createWorkflowConnection, type WorkflowConnection } from '$lib/ws';
  import StepRenderer from '$lib/components/StepRenderer.svelte';
  import type { StepState, WsStatus } from '$lib/workflow-types';
  import { Alert, AlertDescription } from '$lib/components/ui/alert';
  import { Spinner } from '$lib/components/ui/spinner';
  import ShaderBackground from '$lib/components/ShaderBackground.svelte';
  import { fly } from 'svelte/transition';

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
  const isIdle = $derived(workflowState.status === 'idle');

  // ── Blend : 0 = dark shader, 1 = vague élargie = blanc ──────────────────
  let shaderBlend = $state(0);
  $effect(() => {
    const target = isIdle ? 0 : 1;
    const duration = isIdle ? 80 : 80;
    const start = performance.now();
    const from = shaderBlend;
    let raf: number;
    function tick(now: number) {
      const t = Math.min((now - start) / duration, 1);
      const e = t < 0.5 ? 2*t*t : -1+(4-2*t)*t;
      shaderBlend = from + (target - from) * e;
      if (t < 1) raf = requestAnimationFrame(tick);
    }
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
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
    workflowState.steps = [];
    workflowState.errorMsg = '';
    workflowState.runId = '';

    conn = createWorkflowConnection(WS_URL, {
      onStatusChange(status) { workflowState.status = status; },
      onError(err) { workflowState.errorMsg = err; },
      onMessage(msg) {
        if (msg.type === 'workflow_started') {
          workflowState.totalSteps = msg.total_steps;
        } else if (msg.type === 'step_activated') {
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
          updateStep(msg.step_id, { status: 'complete', component_type: msg.component_type, data: msg.data as Record<string, unknown> });
        } else if (msg.type === 'confirmation_request') {
          updateStep(msg.step_id, { status: 'confirmation', component_type: msg.component_type, data: msg.data as Record<string, unknown> });
        } else if (msg.type === 'step_error') {
          updateStep(msg.step_id, { status: 'error', error: msg.error });
          workflowState.errorMsg = msg.error;
        } else if (msg.type === 'workflow_complete') {
          workflowState.runId = msg.run_id;
          workflowState.status = 'closed';
        }
      },
    });

    conn.send({ type: 'start', description: workflowState.description });
  }

  function handleStepAction(action: object) {
    conn?.send(action);
    const a = action as { type: string; step_id?: string };
    if (a.type === 'confirmation' && a.step_id) updateStep(a.step_id, { status: 'complete' });
  }

  function reset() {
    conn?.close();
    conn = null;
    workflowState = { status: 'idle', description: '', totalSteps: 0, steps: [], activeStepId: '', errorMsg: '', runId: '' };
  }

  const HIDDEN_STEPS = new Set(['product_description', 'ai_analysis']);
  const visibleSteps = $derived(
    workflowState.steps.filter((s) => !HIDDEN_STEPS.has(s.step_id))
  );

  $effect(() => () => conn?.close());
</script>

<main class="max-w-2xl mx-auto py-8 px-4">
  <header class="flex justify-between items-center mb-6">
    <h1 class="text-xl font-bold">Guided Analysis</h1>
    <a href="/" class="text-sm text-primary hover:underline">← Home</a>
  </header>

  {#if workflowState.status === 'idle'}
    <form onsubmit={startWorkflow} class="flex gap-2 mb-4">
      <Input
        type="text"
        bind:value={workflowState.description}
        placeholder="Describe your product idea…"
        aria-label="Product description"
        class="flex-1"
      />
      <Button type="submit" disabled={!workflowState.description.trim()}>Start</Button>
    </form>
  {:else}
    {#if workflowState.errorMsg}
      <Alert variant="destructive" class="mb-6">
        <AlertDescription>{workflowState.errorMsg}</AlertDescription>
      </Alert>
    {/if}

    <div class="flex flex-col gap-8">
      {#each visibleSteps as step (step.step_id)}
        {#if step.status === 'processing' && !step.component_type}
          <div class="flex items-center gap-2 text-sm text-muted-foreground">
            <Spinner class="w-4 h-4" />
            <span>{step.label}…</span>
          </div>
        {:else if step.component_type && step.status !== 'error'}
          <StepRenderer
            componentType={step.component_type}
            data={step.data ?? {}}
            tokens={step.tokens}
            stepId={step.step_id}
            status={step.status}
            onAction={handleStepAction}
          />
        {:else if step.status === 'error'}
          <p class="text-destructive text-sm">{step.error}</p>
        {/if}
      {/each}
    </div>

    {#if workflowState.runId}
      <div class="mt-8 pt-6 border-t flex items-center justify-between">
        <p class="text-sm text-muted-foreground">Analysis complete</p>
        <Button onclick={reset}>Start new analysis</Button>
      </div>
    {/if}
  {/if}

</div>

<style>
  :global(body) {
    margin: 0; padding: 0;
    background: #f7f7fc;
    font-family: system-ui, -apple-system, sans-serif;
  }

  /* ── Durée de transition globale pour le thème ── */
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
    color: #1e293b;
    transition: opacity 0.6s ease 0.5s, color var(--theme-dur) ease;
  }
  .logo-topleft.visible { opacity: 1; pointer-events: auto; }
  .logo-topleft.visible { color: #3b82f6; }
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
    transition:
      border-color 0.2s,
      background var(--theme-dur) ease;
  }
  .search-bar:focus-within { border-color: #3b82f6; }
  .dark .search-bar {
    background: rgba(15, 23, 42, 0.85);
    border-color: #334155;
  }
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
  input::placeholder { color: #94a3b8; transition: color var(--theme-dur) ease; }
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
  }
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
    max-height: 4rem;
    opacity: 1;
    transition: max-height 0.7s ease, opacity 0.35s ease, margin 0.7s ease;
    margin-top: 0;
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
  .dark .chip {
    background: rgba(255,255,255,0.06);
    border-color: rgba(255,255,255,0.12);
    color: #cbd5e1;
  }
  .dark .chip:hover { background: rgba(124,58,237,0.2); border-color: #7c3aed; color: #fff; }

  /* ── Steps main ── */
  main {
    position: relative;
    z-index: 1;
    width: min(720px, calc(100% - 4rem));
    margin: 0 auto;
    padding: 7rem 0 4rem;
  }

  .step-counter {
    font-size: 0.8rem;
    color: #94a3b8;
    margin: 0 0 1.25rem;
  }

  .steps-list { display: flex; flex-direction: column; gap: 0.75rem; }

  /* ── Step card ── */
  .step {
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(8px);
    transition:
      background var(--theme-dur) ease,
      border-color var(--theme-dur) ease;
  }
  .dark .step {
    background: rgba(15, 23, 42, 0.7);
    border-color: #1e293b;
  }

  .step-active    { border-color: #3b82f6 !important; }
  .step-processing{ border-color: #f59e0b !important; }
  .step-error     { border-color: #ef4444 !important; }
  .dark .step-active    { border-color: #7c3aed !important; }
  .dark .step-processing{ border-color: #eab308 !important; }

  .step-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.65rem 1rem;
    background: rgba(0,0,0,0.02);
    transition: background var(--theme-dur) ease;
  }
  .dark .step-header { background: rgba(255,255,255,0.03); }

  .step-active    .step-header { background: rgba(59,130,246,0.07) !important; }
  .step-processing .step-header { background: rgba(245,158,11,0.06) !important; }
  .dark .step-active    .step-header { background: rgba(124,58,237,0.08) !important; }
  .dark .step-processing .step-header { background: rgba(234,179,8,0.06) !important; }

  .step-num {
    background: #3b82f6;
    color: #fff;
    width: 1.4rem; height: 1.4rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    font-weight: 700;
    flex-shrink: 0;
    transition: background var(--theme-dur) ease;
  }
  .dark .step-num { background: #7c3aed; }

  .step-label {
    font-size: 0.875rem; font-weight: 500; flex: 1;
    color: #1e293b;
    transition: color var(--theme-dur) ease;
  }
  .dark .step-label { color: #e2e8f0; }

  .step-body  { padding: 0.75rem 1rem; }
  .step-error-msg { padding: 0.5rem 1rem; font-size: 0.85rem; color: #f87171; }
</style>
