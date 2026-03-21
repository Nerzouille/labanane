<svelte:options runes={true} />
<script lang="ts">
  import { createWorkflowConnection, type WorkflowConnection } from '$lib/ws';
  import StepRenderer from '$lib/components/StepRenderer.svelte';
  import type { StepState, WsStatus } from '$lib/workflow-types';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Alert, AlertDescription } from '$lib/components/ui/alert';
  import { Badge } from '$lib/components/ui/badge';
  import { Spinner } from '$lib/components/ui/spinner';

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
      onStatusChange(status) {
        workflowState.status = status;
      },
      onError(err) {
        workflowState.errorMsg = err;
      },
      onMessage(msg) {
        if (msg.type === 'workflow_started') {
          workflowState.totalSteps = msg.total_steps;
        } else if (msg.type === 'step_activated') {
          const s = findOrCreateStep(msg.step_id);
          s.step_number = msg.step_number;
          s.label = msg.label;
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
    const a = action as { type: string; step_id?: string; confirmed?: boolean };
    if (a.type === 'confirmation' && a.step_id) {
      updateStep(a.step_id, { status: 'complete' });
    }
  }

  function reset() {
    conn?.close();
    conn = null;
    workflowState = {
      status: 'idle',
      description: '',
      totalSteps: 0,
      steps: [],
      activeStepId: '',
      errorMsg: '',
      runId: '',
    };
  }

  $effect(() => () => conn?.close());
</script>

<main class="max-w-2xl mx-auto py-8 px-4">
  <header class="flex justify-between items-center mb-6">
    <h1 class="text-xl font-bold">Guided Analysis</h1>
    <a href="/" class="text-sm text-primary hover:underline">← Home</a>
  </header>

  {#if workflowState.status === 'idle' || workflowState.status === 'closed'}
    {#if workflowState.status === 'closed'}
      <Alert class="mb-4 border-green-500 bg-green-50 text-green-800">
        <AlertDescription>✓ Workflow complete — run: <code class="font-mono text-xs">{workflowState.runId}</code></AlertDescription>
      </Alert>
      <Button onclick={reset}>Start new analysis</Button>
    {:else}
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
    {/if}
  {:else}
    {#if workflowState.totalSteps > 0}
      <p class="text-sm text-muted-foreground mb-4">
        Step {workflowState.steps.filter((s) => s.status === 'complete' || s.status === 'confirmation').length}
        / {workflowState.totalSteps}
      </p>
    {/if}

    {#if workflowState.errorMsg}
      <Alert variant="destructive" class="mb-4">
        <AlertDescription>{workflowState.errorMsg}</AlertDescription>
      </Alert>
    {/if}

    <div class="flex flex-col gap-3">
      {#each workflowState.steps as step (step.step_id)}
        {@const borderClass = step.status === 'active' ? 'border-primary' : step.status === 'processing' ? 'border-yellow-400' : step.status === 'error' ? 'border-destructive' : 'border-border'}
        {@const headerClass = step.status === 'active' ? 'bg-primary/10' : step.status === 'processing' ? 'bg-yellow-50' : 'bg-muted/50'}
        <section class="border rounded-lg overflow-hidden {borderClass}">
          <div class="flex items-center gap-2 px-3 py-2 {headerClass}">
            <span class="bg-primary text-primary-foreground w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0">
              {step.step_number}
            </span>
            <span class="font-medium text-sm flex-1">{step.label}</span>
            {#if step.status === 'processing'}
              <Spinner class="w-4 h-4 text-yellow-500" />
            {/if}
            {#if step.status === 'complete'}
              <Badge variant="secondary" class="text-xs">Done</Badge>
            {/if}
          </div>

          {#if (step.status === 'result' || step.status === 'complete' || step.status === 'confirmation') && step.component_type}
            <div class="p-3">
              <StepRenderer
                componentType={step.component_type}
                data={step.data ?? {}}
                tokens={step.tokens}
                stepId={step.step_id}
                onAction={handleStepAction}
              />
            </div>
          {/if}

          {#if step.status === 'error'}
            <p class="text-destructive text-sm px-3 py-2">{step.error}</p>
          {/if}
        </section>
      {/each}
    </div>
  {/if}
</main>
