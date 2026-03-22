# labanane Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-22

## Active Technologies
- Python 3.12 (backend), TypeScript / Svelte 5 (frontend) + FastAPI (WebSocket), pydantic v2, uv (backend); SvelteKit, bun, shadcn-svelte (frontend) (002-guided-analysis-workflow)
- In-memory session state only (no database); `WorkflowRun` dict keyed by session ID (002-guided-analysis-workflow)
- In-memory only — `WorkflowRun` dict keyed by `run_id`; deleted on WebSocket disconnect. Report markdown stored in-memory keyed by `run_id` until disconnect. (003-market-analysis-platform)
- TypeScript / Svelte 5 (runes mode) + SvelteKit, shadcn-svelte, `@hugeicons/svelte`, Svelte built-in transitions (`fly`, `slide`, `fade`) (004-workflow-ux-improvements)
- N/A — in-memory state only (`workflowState` in `+page.svelte`) (004-workflow-ux-improvements)

- Python 3.12 (backend) · TypeScript / Svelte 5 (frontend) (001-market-intelligence-mvp)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.12 (backend) · TypeScript / Svelte 5 (frontend): Follow standard conventions

## Recent Changes
- 004-workflow-ux-improvements: Added TypeScript / Svelte 5 (runes mode) + SvelteKit, shadcn-svelte, `@hugeicons/svelte`, Svelte built-in transitions (`fly`, `slide`, `fade`)
- 003-market-analysis-platform: Added Python 3.12 (backend) · TypeScript / Svelte 5 (frontend)
- 002-guided-analysis-workflow: Added Python 3.12 (backend), TypeScript / Svelte 5 (frontend) + FastAPI (WebSocket), pydantic v2, uv (backend); SvelteKit, bun, shadcn-svelte (frontend)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
