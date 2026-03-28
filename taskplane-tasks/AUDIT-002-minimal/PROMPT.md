# Task: AUDIT-002 — Add Architecture Section

**Created:** 2026-03-28
**Size:** S

## Review Level: 0 (None)

**Assessment:** Minimal documentation update to explain .pi/ directory.
**Score:** N/A

## Mission

Add a small "Architecture" section to README.md that explains the .pi/ directory structure.

## Expected Changes

Add this section to README.md:

```markdown
## Architecture

### Task Automation (Optional)

This project uses Taskplane for task-based automation:

- **Task Areas:** Located in `taskplane-tasks/`
- **Task Runner:** Configured in `.pi/task-runner.yaml`
- **Orchestrator:** Configured in `.pi/task-orchestrator.yaml`

See `.pi/CONTEXT.md` for task automation documentation.
```

## Dependencies

- **None**

## Environment

- **Workspace:** Project root
- **Services required:** None

## File Scope

- `README.md`

## Steps

### Step 0: Preflight

- [ ] Verify this PROMPT.md is readable
- [ ] Verify STATUS.md exists in the same folder

### Step 1: Add Architecture Section

- [ ] Insert the Architecture section after "## Environment Variables"
- [ ] Use proper markdown formatting

### Step 2: Verification

- [ ] Verify README.md contains the new section
- [ ] Verify formatting is correct

### Step 3: Delivery

## Completion Criteria

- [ ] Architecture section added to README.md
- [ ] Section is properly formatted
- [ ] .DONE file created

## Git Commit Convention

- **Implementation:** `docs(AUDIT-002): add architecture section`

## Do NOT

- Modify any other files
- Change existing content

---

## Amendments (Added During Execution)

<!-- Workers add amendments here if issues discovered during execution. -->
