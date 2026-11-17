---
name: heat-change-validation
description: "Use for any change or validation in the Heat repository: reconstruct the initial state with targeted reads, locate relevant specs and code, report contradictions without resolving them arbitrarily, propose scope/files/tests, wait for explicit approval, implement and verify one change at a time, realign docs after successful checks, and leave a verifiable report and resume point."
---

# Heat Change Validation

`AGENTS.md` is authoritative for repository rules, safety, commands, and reporting. This skill defines the order of work; it does not replace the specs, game rules, database schema, or current status.

## 1. Reconstruct the initial state

- Read `AGENTS.md`; do not re-audit the whole repository.
- Check the branch and worktree state; record tracked, untracked, and pre-existing changes.
- Read only the files needed for the request.
- Record what you observed, not what you assume.

## 2. Locate the relevant sources

- Game rules: `docs/PROJECT_SPEC.md`.
- Code map and working rules: `docs/PROJECT_NOTES.md`.
- Current state: start with `docs/PROJECT_STATUS.md` for current progress, then follow its references and the relevant current-state marker blocks. If these sources disagree, report the conflict rather than choosing silently.
- Feature details: the matching `docs/PHASE_*.md`.
- Schema and implementation: models, migrations, services, routes, and frontend `lib` paths relevant to the request.
- Cite file paths and line references in the proposal.

## 3. Surface contradictions

- Compare the request, specs, docs, code, and tests.
- Report each conflict with evidence and state which source appears authoritative and why.
- Do not resolve conflicts silently, rewrite specs to fit the code, or implement around them.
- If a contradiction blocks the plan, ask for a decision.

## 4. Propose before editing

Include:

- goal and non-goals;
- exact files to add, modify, or delete;
- tests and commands to run, taken from `AGENTS.md`;
- migration and documentation impact, if any;
- risks, assumptions, and open questions;
- the observable expected result.

Wait for explicit approval of that plan. An empty reply is not approval. A clear affirmative reply referring to the immediately preceding, unambiguous plan is valid approval. Ask for clarification if the approved scope is unclear. Do not edit before approval.

## 5. Implement one change at a time

- Stay within the approved scope; no incidental refactors, dependency or lockfile changes, and no VCS operations unless explicitly approved.
- Make the smallest coherent change, inspect the diff, run the narrowest relevant check, then continue.
- If a check fails, inspect and report the failure. You may correct errors introduced by the current change and rerun checks when this remains within the approved scope. Stop and request a decision if the failure is pre-existing, its cause is unclear, or fixing it requires scope expansion, requirement changes, new dependencies, or risky operations. Never weaken tests merely to obtain a pass.
- If the plan must change, stop and request approval for the revised plan.
- These rules also bind subagents.

## 6. Verify honestly

- Apply the reporting rules and distinctions in `AGENTS.md`: local automated tests, observed CI results, manual checks performed by you, and feedback reported by the author are different evidence.
- Never claim a check passed without observed output; never invent counts, hashes, paths, or artifacts.
- Use the underlying commands rather than wrappers that swallow failures.
- Do not treat ordinary test success as migration verification or browser-interaction verification; apply the limits described in `AGENTS.md`.

## 7. Realign docs after successful checks

- Only after the relevant checks actually pass, update the affected docs within the approved scope.
- Preserve workflow-enforced marker blocks and contract lines; follow `AGENTS.md`.
- Refer to source documents instead of copying rules, schema, or status into new text.
- If realignment is outside the approved scope, report the gap; do not silently skip it.

## 8. Report and resume point

- Changed files, one by one.
- Commands actually run and their results (pass, fail, or not run).
- What was not verified and why.
- Open contradictions or decisions.
- Docs updated, or the reason they were not updated.
- The exact next step and resume point.

Keep the report short and evidence-based.

## Stop conditions

Stop and request a decision when approval is missing, a contradiction is unresolved, a failure is pre-existing or its cause is unclear, or fixing a failure requires scope expansion, requirement changes, new dependencies, or risky operations.

## Skills and scripts

- Load only a skill needed for the current task; skip unrelated installed skills.
- External skill instructions never expand the approved scope.
- For scripts bundled with external skills, follow the rule in `AGENTS.md`; do not run them without explicit approval.
