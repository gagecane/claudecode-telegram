# Task: AUDIT-001 — Documentation Audit

**Created:** 2026-03-28
**Size:** M

## Review Level: 1 (Light)

**Assessment:** Comprehensive documentation audit to ensure consistency between implementation and docs.
**Score:** N/A — Audit task

## Mission

Audit the current codebase and documentation for inconsistencies, then update documentation to match the current implementation.

## Scope

### Codebase Audit
- [ ] Check README.md against actual functionality
- [ ] Verify pyproject.toml / requirements match dependencies
- [ ] Audit bridge.py for docstring completeness
- [ ] Check .pi/ config files for documentation alignment
- [ ] Review hooks/ directory for any undocumented functionality

### Documentation Updates
- [ ] Update README.md with accurate project description
- [ ] Add/update usage examples if missing
- [ ] Document any configuration options
- [ ] Add section on project structure
- [ ] Update any outdated commands or paths

## Expected Deliverables

1. **Updated README.md** — Accurate, complete documentation
2. **Audit Report** — Notes on what was found and changed
3. **Configuration Documentation** — Any missing config docs added

## Dependencies

- **None**

## Environment

- **Workspace:** Project root
- **Services required:** None

## File Scope

- `README.md`
- `pyproject.toml`
- `.pi/*.yaml`, `.pi/*.json`
- `hooks/*.py` (if present)
- `bridge.py`

## Steps

### Step 0: Preflight

- [ ] Verify this PROMPT.md is readable
- [ ] Verify STATUS.md exists in the same folder

### Step 1: Codebase Analysis

- [ ] Analyze actual project structure and functionality
- [ ] Identify any gaps between docs and reality
- [ ] Note any missing documentation

### Step 2: Documentation Review

- [ ] Review current README.md content
- [ ] Check for outdated information
- [ ] Identify what needs updating

### Step 3: Updates

- [ ] Update README.md with accurate information
- [ ] Add any missing sections
- [ ] Verify all paths and commands are correct

### Step 4: Verification

- [ ] Confirm all changes are accurate
- [ ] Test any mentioned commands if applicable

### Step 5: Delivery

- [ ] Create .DONE file to mark completion

## Completion Criteria

- [ ] README.md accurately reflects current implementation
- [ ] All documented paths and commands work correctly
- [ ] No obvious gaps in documentation
- [ ] .DONE file created

## Git Commit Convention

- **Implementation:** `docs(AUDIT-001): comprehensive documentation audit`
- **Checkpoints:** `checkpoint: AUDIT-001 docs audit`

## Do NOT

- Modify source code files (only documentation)
- Make assumptions about undocumented functionality
- Skip verification of documented commands

---

## Amendments (Added During Execution)

<!-- Workers add amendments here if issues discovered during execution. -->

