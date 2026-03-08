# Migration Plan: Quality Scoring & Session Logging

**Date:** 2026-03-08
**Status:** DRAFT
**Target:** D:/claude_code/paper-to-beamer
**Source:** D:/claude_code/my-project

---

## Objective

Migrate three key features from my-project to paper-to-beamer:
1. Quality scoring system for Beamer .tex files
2. Session logging infrastructure for GitHub update logs
3. Useful skills (proofread, context-status, learn, compile-latex, commit)

---

## Feature 1: Quality Scoring System

### Overview

`scripts/quality_score.py` provides objective quality scoring (0-100) for Beamer .tex files with three quality gates:
- 80/100: Commit threshold (blocks if below)
- 90/100: PR threshold (warning if below)
- 95/100: Excellence (aspirational)

### What It Checks for Beamer Files

**Critical Issues (auto-fail or heavy penalties):**
- LaTeX syntax errors (unmatched environments, unclosed braces)
- Undefined citations (citation keys not in bibliography)
- Overfull hbox warnings (content overflow)
- Equation overflow (single line >120 chars)

**Major Issues:**
- Text overflow (lines >120 chars in frames)
- Notation inconsistency

**Minor Issues:**
- Font size reductions

### Files to Copy

| Source | Destination | Action |
|--------|-------------|--------|
| `scripts/quality_score.py` | `scripts/quality_score.py` | Copy entire file |

### Modifications Needed

**Line 512-515:** Update bibliography path detection
```python
# Current (my-project):
bib_file = self.filepath.parent.parent / 'Bibliography_base.bib'
if not bib_file.exists():
    bib_file = self.filepath.parent / 'Bibliography_base.bib'

# Modified (paper-to-beamer):
# paper-to-beamer doesn't use centralized bibliography
# Each paper may have its own .bib file or none
bib_file = self.filepath.with_suffix('.bib')
if not bib_file.exists():
    # Check for common bibliography names in same directory
    for bib_name in ['references.bib', 'bibliography.bib', 'refs.bib']:
        candidate = self.filepath.parent / bib_name
        if candidate.exists():
            bib_file = candidate
            break
```

**Lines 28-48, 50-65:** Remove Quarto and R rubrics (not used in paper-to-beamer)
- Keep only `BEAMER_RUBRIC` (lines 67-80)
- Keep `THRESHOLDS` (lines 82-86)

**Lines 386-447:** Remove `score_quarto()` method (not used)

**Lines 449-490:** Remove `score_r_script()` method (not used)

**Lines 728-736:** Update CLI to only support .tex files
```python
# Remove these branches:
if filepath.suffix == '.qmd':
    report = scorer.score_quarto()
elif filepath.suffix == '.R':
    report = scorer.score_r_script()

# Keep only:
if filepath.suffix == '.tex':
    report = scorer.score_beamer()
else:
    print(f"Error: Only .tex files supported in paper-to-beamer")
    continue
```

### Dependencies

**Python packages required:**
- Standard library only (no external dependencies)
- Uses: `sys`, `argparse`, `subprocess`, `pathlib`, `re`, `json`

### Testing Steps

1. Create test .tex file with known issues:
   - Unclosed `\begin{frame}` environment
   - Citation to non-existent key
   - Line >120 chars in frame
   - Long equation

2. Run quality scorer:
   ```bash
   cd D:/claude_code/paper-to-beamer
   python scripts/quality_score.py Slides/test.tex
   ```

3. Verify output shows:
   - Score < 100 (penalties applied)
   - Critical issues listed with line numbers
   - Status: BLOCKED or COMMIT_READY

4. Fix issues and re-run to verify score improves

---

## Feature 2: Session Logging Infrastructure

### Overview

Session logging provides structured documentation for:
- GitHub update logs (what changed and why)
- Design decisions and rationale
- Incremental work tracking
- Learnings and corrections
- Verification results

### Files to Copy

| Source | Destination | Action |
|--------|-------------|--------|
| `templates/session-log.md` | `templates/session-log.md` | Copy as-is |
| `templates/quality-report.md` | `templates/quality-report.md` | Copy as-is |
| `.claude/rules/session-logging.md` | `.claude/rules/session-logging.md` | Copy as-is |

### Directory Structure to Create

```bash
mkdir -p quality_reports/session_logs
mkdir -p quality_reports/merges
mkdir -p quality_reports/plans
mkdir -p templates
```

### Modifications Needed

**None required** — templates and rules are generic and work as-is.

### Usage Pattern

**1. Post-Plan Log (after plan approval):**
```bash
# Create: quality_reports/session_logs/2026-03-08_paper-extraction.md
# Capture: goal, approach, rationale, key context
```

**2. Incremental Logging (during work):**
```markdown
## Incremental Work Log

**18:30 UTC:** Extracted tables from Smith2020.pdf using pdfplumber
**18:45 UTC:** Fixed coordinate detection for rotated tables
**19:00 UTC:** Generated Beamer slides with 12 frames
```

**3. End-of-Session Log (when wrapping up):**
```markdown
## Summary
Completed paper-to-beamer conversion for Smith2020.pdf.
Quality score: 85/100 (commit-ready).

## Open Questions
- [ ] Should we auto-detect table captions or require manual annotation?
```

### Testing Steps

1. Create a test session log:
   ```bash
   cp templates/session-log.md quality_reports/session_logs/2026-03-08_test-session.md
   ```

2. Fill in sections during a real task

3. Verify it's useful for:
   - GitHub commit messages (copy from "Changes Made")
   - Future reference (read "Learnings & Corrections")
   - Resuming after context compression (read "Next Steps")

---

## Feature 3: Skills Migration

### Skills to Migrate

| Skill | Priority | Reason |
|-------|----------|--------|
| `compile-latex` | HIGH | Core workflow — compile Beamer with XeLaTeX |
| `beamer-overflow-fix` | HIGH | Already exists, check for updates |
| `proofread` | MEDIUM | Grammar/typo checking for slides |
| `context-status` | MEDIUM | Monitor context usage |
| `learn` | MEDIUM | Extract discoveries into persistent skills |
| `commit` | LOW | Standard git workflow (already exists in paper-to-beamer?) |

### Skill 1: compile-latex (HIGH PRIORITY)

**Source:** `.claude/skills/compile-latex/SKILL.md`

**Destination:** `.claude/skills/compile-latex/SKILL.md`

**Modifications:**

Line 18-22: Update TEXINPUTS path separator for Windows
```bash
# Current (my-project, macOS):
TEXINPUTS=../Preambles:$TEXINPUTS xelatex -interaction=nonstopmode $ARGUMENTS.tex

# Modified (paper-to-beamer, Windows):
TEXINPUTS="../Preambles;$TEXINPUTS" xelatex -interaction=nonstopmode $ARGUMENTS.tex
```

Lines 19, 27: Remove bibtex steps (paper-to-beamer doesn't use centralized bibliography)
```bash
# Remove this line:
BIBINPUTS=..:$BIBINPUTS bibtex $ARGUMENTS

# Simplify to 2-pass compilation:
cd Slides
TEXINPUTS="../Preambles;$TEXINPUTS" xelatex -interaction=nonstopmode $ARGUMENTS.tex
TEXINPUTS="../Preambles;$TEXINPUTS" xelatex -interaction=nonstopmode $ARGUMENTS.tex
```

Lines 48-52: Update "Why 3 passes?" section
```markdown
## Why 2 passes?
1. First xelatex: Creates initial PDF with placeholders
2. Second xelatex: Resolves all cross-references with final page numbers

(No bibtex needed — paper-to-beamer embeds citations directly in slides)
```

Lines 54-56: Remove BIBINPUTS note
```markdown
## Important
- **Always use XeLaTeX**, never pdflatex
- **TEXINPUTS** is required: your Beamer theme lives in `Preambles/`
```

**Testing:**
```bash
cd D:/claude_code/paper-to-beamer
# Invoke skill via Claude Code:
/compile-latex test_file
```

### Skill 2: beamer-overflow-fix (CHECK FOR UPDATES)

**Current status:** Already exists in paper-to-beamer

**Action:** Compare my-project version with paper-to-beamer version

**Source:** `.claude/skills/beamer-overflow-fix/SKILL.md` (my-project)

**Comparison needed:**
1. Read both versions
2. Check if my-project has newer fixes or strategies
3. If yes, merge improvements into paper-to-beamer version
4. If no, keep paper-to-beamer version as-is

**Key sections to compare:**
- Fix strategies (lines 34-41 in my-project version)
- Priority order (lines 134-139)
- Escalation logic (lines 127-132)

### Skill 3: proofread (MEDIUM PRIORITY)

**Source:** `.claude/skills/proofread/SKILL.md`

**Destination:** `.claude/skills/proofread/SKILL.md`

**Modifications:**

Line 16: Update file location pattern
```markdown
# Current:
- If `$ARGUMENTS` is "all": review all lecture files in `Slides/` and `Quarto/`

# Modified:
- If `$ARGUMENTS` is "all": review all Beamer files in `Slides/`
```

Lines 32-34: Update report save location
```markdown
# Current:
- For `.tex` files: `quality_reports/FILENAME_report.md`
- For `.qmd` files: `quality_reports/FILENAME_qmd_report.md`

# Modified:
- For `.tex` files: `quality_reports/FILENAME_proofread.md`
```

**Testing:**
```bash
/proofread Smith2020.tex
# Check that quality_reports/Smith2020_proofread.md is created
```

### Skill 4: context-status (MEDIUM PRIORITY)

**Source:** `.claude/skills/context-status/SKILL.md`

**Destination:** `.claude/skills/context-status/SKILL.md`

**Modifications:** None required (generic skill)

**Testing:**
```bash
/context-status
# Should show: context usage, active plan, session log, preservation state
```

### Skill 5: learn (MEDIUM PRIORITY)

**Source:** `.claude/skills/learn/SKILL.md`

**Destination:** `.claude/skills/learn/SKILL.md`

**Modifications:** None required (generic skill)

**Usage example:**
```bash
# After discovering a non-obvious fix:
/learn pdf-table-extraction-rotated
# Creates: .claude/skills/pdf-table-extraction-rotated/SKILL.md
```

### Skill 6: commit (LOW PRIORITY)

**Action:** Check if paper-to-beamer already has a commit skill

**If missing:** Copy from my-project with no modifications (generic git workflow)

**If exists:** Compare versions and merge any improvements

---

## Migration Checklist

### Phase 1: Quality Scoring System

- [ ] Copy `scripts/quality_score.py` to paper-to-beamer
- [ ] Modify bibliography path detection (lines 512-515)
- [ ] Remove Quarto/R rubrics and methods
- [ ] Update CLI to only support .tex files
- [ ] Create test .tex file with known issues
- [ ] Run quality scorer and verify output
- [ ] Fix test issues and verify score improves
- [ ] Document usage in CLAUDE.md

### Phase 2: Session Logging Infrastructure

- [ ] Create directory structure:
  - `quality_reports/session_logs/`
  - `quality_reports/merges/`
  - `quality_reports/plans/`
  - `templates/`
- [ ] Copy `templates/session-log.md`
- [ ] Copy `templates/quality-report.md`
- [ ] Copy `.claude/rules/session-logging.md`
- [ ] Create test session log
- [ ] Verify template is useful for real task
- [ ] Document usage in CLAUDE.md

### Phase 3: Skills Migration

**High Priority:**
- [ ] Migrate `compile-latex` skill
  - [ ] Update TEXINPUTS path separator for Windows
  - [ ] Remove bibtex steps
  - [ ] Update documentation
  - [ ] Test compilation
- [ ] Compare `beamer-overflow-fix` versions
  - [ ] Read both versions
  - [ ] Merge improvements if needed
  - [ ] Test overflow detection and fixes

**Medium Priority:**
- [ ] Migrate `proofread` skill
  - [ ] Update file location patterns
  - [ ] Update report save location
  - [ ] Test proofreading
- [ ] Migrate `context-status` skill
  - [ ] Copy as-is
  - [ ] Test status reporting
- [ ] Migrate `learn` skill
  - [ ] Copy as-is
  - [ ] Test skill creation

**Low Priority:**
- [ ] Check if `commit` skill exists
- [ ] Copy or merge if needed
- [ ] Test git workflow

### Phase 4: Documentation & Integration

- [ ] Update `CLAUDE.md` with new features:
  - Quality scoring usage
  - Session logging triggers
  - New skills reference
- [ ] Update `README.md` if needed
- [ ] Create example session log
- [ ] Create example quality report
- [ ] Test full workflow: paper → beamer → quality score → session log

### Phase 5: Verification

- [ ] Run quality scorer on existing Beamer files
- [ ] Create session log for a real task
- [ ] Use new skills in actual workflow
- [ ] Verify all paths are correct (Windows vs Unix)
- [ ] Verify no hardcoded paths from my-project
- [ ] Commit changes with quality score >= 80

---

## File Copy Summary

### Direct Copies (No Modifications)

```bash
# Templates
cp my-project/templates/session-log.md paper-to-beamer/templates/
cp my-project/templates/quality-report.md paper-to-beamer/templates/

# Rules
cp my-project/.claude/rules/session-logging.md paper-to-beamer/.claude/rules/

# Skills (generic)
cp -r my-project/.claude/skills/context-status paper-to-beamer/.claude/skills/
cp -r my-project/.claude/skills/learn paper-to-beamer/.claude/skills/
```

### Copies with Modifications

```bash
# Quality scorer (modify bibliography detection, remove Quarto/R)
cp my-project/scripts/quality_score.py paper-to-beamer/scripts/
# Then edit: lines 28-65 (remove rubrics), 386-490 (remove methods), 512-515 (bib path), 728-736 (CLI)

# Skills (modify paths/commands)
cp -r my-project/.claude/skills/compile-latex paper-to-beamer/.claude/skills/
# Then edit: lines 18-22 (TEXINPUTS), 19,27 (remove bibtex), 48-52 (update docs), 54-56 (remove BIBINPUTS)

cp -r my-project/.claude/skills/proofread paper-to-beamer/.claude/skills/
# Then edit: line 16 (file locations), lines 32-34 (report paths)
```

### Conditional Copies (Check First)

```bash
# Compare versions before copying
diff my-project/.claude/skills/beamer-overflow-fix/SKILL.md \
     paper-to-beamer/.claude/skills/beamer-overflow-fix/SKILL.md

# Check if commit skill exists
ls paper-to-beamer/.claude/skills/commit/
# If missing: cp -r my-project/.claude/skills/commit paper-to-beamer/.claude/skills/
```

---

## Expected Outcomes

### Quality Scoring System

**Before migration:**
- No objective quality measurement
- Manual checking for overflow/errors
- Inconsistent commit quality

**After migration:**
- Automated quality scoring (0-100)
- Enforced quality gates (80/90/95)
- Objective criteria for commits
- Faster issue detection

### Session Logging

**Before migration:**
- Ad-hoc commit messages
- Lost context after compression
- Difficult to track design decisions

**After migration:**
- Structured session logs
- Persistent design rationale
- Easy GitHub update logs
- Context survival across sessions

### Skills

**Before migration:**
- Manual LaTeX compilation
- Inconsistent overflow fixes
- No context monitoring
- Lost discoveries

**After migration:**
- One-command compilation (`/compile-latex`)
- Systematic overflow fixes (`/beamer-overflow-fix`)
- Context usage monitoring (`/context-status`)
- Persistent skill extraction (`/learn`)
- Automated proofreading (`/proofread`)

---

## Risks & Mitigations

### Risk 1: Path Separator Differences (Windows vs Unix)

**Issue:** my-project uses `:` (Unix), paper-to-beamer needs `;` (Windows)

**Mitigation:**
- Carefully update all TEXINPUTS paths in compile-latex skill
- Test compilation on Windows before committing
- Document path separator in CLAUDE.md

### Risk 2: Bibliography Handling Differences

**Issue:** my-project uses centralized `Bibliography_base.bib`, paper-to-beamer doesn't

**Mitigation:**
- Update quality_score.py to check for per-paper .bib files
- Remove bibtex steps from compile-latex skill
- Test with papers that have/don't have bibliographies

### Risk 3: Skill Conflicts

**Issue:** beamer-overflow-fix already exists in paper-to-beamer

**Mitigation:**
- Compare versions before overwriting
- Merge improvements rather than replace
- Test overflow fixes after merge

### Risk 4: Python Dependencies

**Issue:** quality_score.py might have dependencies not installed

**Mitigation:**
- Verify only standard library is used (no pip install needed)
- Test script before committing
- Document any requirements in README

---

## Timeline Estimate

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1: Quality Scoring | Copy, modify, test | 30-45 minutes |
| Phase 2: Session Logging | Copy templates, create dirs | 15-20 minutes |
| Phase 3: Skills (High) | Migrate 2 skills, test | 30-40 minutes |
| Phase 3: Skills (Medium) | Migrate 3 skills, test | 20-30 minutes |
| Phase 3: Skills (Low) | Check/merge commit | 10-15 minutes |
| Phase 4: Documentation | Update CLAUDE.md, README | 20-30 minutes |
| Phase 5: Verification | End-to-end testing | 30-45 minutes |
| **Total** | | **2.5-3.5 hours** |

---

## Success Criteria

- [ ] Quality scorer runs successfully on paper-to-beamer .tex files
- [ ] Quality scores are accurate (penalties match actual issues)
- [ ] Session log template is useful for real tasks
- [ ] All migrated skills work without errors
- [ ] Compilation skill uses correct Windows paths
- [ ] No hardcoded paths from my-project remain
- [ ] Documentation is updated and accurate
- [ ] Full workflow tested: paper → beamer → score → log → commit

---

## Next Steps After Migration

1. **Use quality scorer before every commit:**
   ```bash
   python scripts/quality_score.py Slides/*.tex
   # Only commit if score >= 80
   ```

2. **Create session logs for significant work:**
   ```bash
   cp templates/session-log.md quality_reports/session_logs/2026-03-08_task.md
   # Update incrementally during work
   ```

3. **Extract learnings into skills:**
   ```bash
   /learn [skill-name]
   # When discovering non-obvious solutions
   ```

4. **Monitor context usage:**
   ```bash
   /context-status
   # Check before long tasks
   ```

5. **Compile with one command:**
   ```bash
   /compile-latex Smith2020
   # Instead of manual 3-pass compilation
   ```

---

## Appendix: Key Code Snippets

### Modified Bibliography Detection (quality_score.py)

```python
def score_beamer(self) -> Dict:
    """Score Beamer/LaTeX lecture slides."""
    content = self.filepath.read_text(encoding='utf-8')

    # ... syntax checks ...

    # Check for undefined/broken citations
    # paper-to-beamer: check for .bib file with same name as .tex
    bib_file = self.filepath.with_suffix('.bib')
    if not bib_file.exists():
        # Check for common bibliography names in same directory
        for bib_name in ['references.bib', 'bibliography.bib', 'refs.bib']:
            candidate = self.filepath.parent / bib_name
            if candidate.exists():
                bib_file = candidate
                break

    broken_citations = IssueDetector.check_broken_citations(content, bib_file)
    # ... rest of scoring ...
```

### Modified Compilation Command (compile-latex skill)

```bash
# paper-to-beamer (Windows, no bibtex)
cd Slides
TEXINPUTS="../Preambles;$TEXINPUTS" xelatex -interaction=nonstopmode $ARGUMENTS.tex
TEXINPUTS="../Preambles;$TEXINPUTS" xelatex -interaction=nonstopmode $ARGUMENTS.tex
```

### Session Log Usage Pattern

```markdown
# Session Log: 2026-03-08 -- Smith2020 Paper Extraction

**Status:** COMPLETED
**Topics:** #paper-to-beamer #table-extraction #beamer

## Objective
Convert Smith2020.pdf to Beamer presentation slides with extracted tables.

## Changes Made

| File | Change | Reason | Quality Score |
|------|--------|--------|---|
| `Slides/Smith2020.tex` | Generated Beamer slides | Paper-to-beamer conversion | 85/100 |
| `Figures/Smith2020_tables/` | Extracted 3 tables as PNG | Table visualization | N/A |

## Incremental Work Log

**18:30 UTC:** Extracted tables using pdfplumber
**18:45 UTC:** Fixed rotated table detection
**19:00 UTC:** Generated 12-frame Beamer presentation
**19:15 UTC:** Fixed 2 overfull hbox warnings
**19:20 UTC:** Quality score: 85/100 (commit-ready)

## Learnings & Corrections

- [LEARN:pdf-extraction] Rotated tables need explicit rotation parameter in pdfplumber
- [LEARN:beamer] Long author lists cause hbox overflow — use \small in title frame

## Verification Results

| Check | Result | Status |
|-------|--------|--------|
| XeLaTeX compilation | 2-pass successful | PASS |
| Overfull warnings | 0 remaining | PASS |
| Quality score | 85/100 | PASS |

## Next Steps

- [x] Commit Smith2020.tex and figures
- [ ] Extract tables from Johnson2021.pdf
```

---

**End of Migration Plan**
