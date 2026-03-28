# TP-002: Verify No Runtime Files Are Committed

## Summary
Run a comprehensive check to ensure no runtime/debug files are tracked in git.

## Context to Read First
- `.gitignore` — verify all patterns are correct
- `.pi/` directory structure
- `taskplane-tasks/` directory structure

## Task Description

Verify that the repository is clean of runtime artifacts:

1. **Check `.pi/` directory** — only config files should be tracked:
   - `.pi/agents/*.md` (agent definitions) ✅
   - `.pi/taskplane-config.json` ✅
   - `.pi/task-orchestrator.yaml` ✅
   - `.pi/task-runner.yaml` ✅
   - `.pi/taskplane.json` — should be IGNORED after TP-001
   - `.pi/batch-history.json` — should be IGNORED
   - `.pi/lane-state-*` — should be IGNORED

2. **Check `taskplane-tasks/`** — only context files should be tracked:
   - `CONTEXT.md` ✅
   - `dependencies.json` ✅
   - Individual task folders (TP-*) — should be IGNORED

3. **Run verification commands**:
   - `git status` — should show clean working tree
   - `git ls-files .pi/` — should only show config files
   - `git ls-files taskplane-tasks/` — should only show CONTEXT.md and dependencies.json

## Acceptance Criteria

1. `git status` shows clean working tree (no uncommitted changes)
2. `git ls-files .pi/` shows only:
   - `.pi/agents/*.md` (4 files)
   - `.pi/taskplane-config.json`
   - `.pi/task-orchestrator.yaml`
   - `.pi/task-runner.yaml`
3. `git ls-files taskplane-tasks/` shows only:
   - `taskplane-tasks/CONTEXT.md`
   - `taskplane-tasks/dependencies.json`
4. Document findings in a brief comment or note

## Notes
- This is a verification task — no file modifications expected
- If issues are found, document them clearly
- Dependencies: Should run AFTER TP-001 completes
