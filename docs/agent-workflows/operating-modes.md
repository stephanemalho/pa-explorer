# Agent Operating Modes And Parallel Workflow

## Agent Operating Modes

### Explore

Read-only. Understand architecture, dependencies, IBM PA flows, and existing decisions.

### Plan

Read-only. Produce an implementation plan, touched files, tests to run, and risks.

### Implement

Edit files only inside the approved scope.

### Review

Read-only. Check correctness, tests, architecture, security, and rule compliance.

### Validate

Run deterministic checks and report exact results.

## Parallel Agent Workflow

- Never run two coding agents in the same worktree.
- Each agent/model must work in its own git worktree and branch.
- Branch format: `agent/<harness>/<ticket-or-task>/<short-slug>`.
- Each worktree must use its own `.env.local`, database name, log folder, temp folder, and ports when applicable.
- Agents may propose changes, but final merge requires human review.
