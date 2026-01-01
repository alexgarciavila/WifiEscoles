# ✅ Task Generation Complete: Tema Oscuro Forzado

**Feature**: 001-dark-theme-mode  
**Generated**: 2025-12-13  
**Time**: ~10 minutos  
**Output**: [tasks.md](tasks.md)

---

## 🎯 Task List Summary

### Total Tasks: **31**

| Phase | Tasks | Description | Duration |
|-------|-------|-------------|----------|
| **Phase 1: Setup** | T001-T002 (2) | Verify dependencies & audit legacy widgets | 5-10 min |
| **Phase 2: Foundational** | T003-T009 (7) | Create theme module with constants & setup function | 20-30 min |
| **Phase 3: User Story 1 (P1)** 🎯 | T010-T015 (6) | Apply dark theme at app startup | 45-60 min |
| **Phase 4: User Story 2 (P2)** | T016-T023 (8) | Validate contrast & legibility | 60-90 min |
| **Phase 5: Polish** | T024-T031 (8) | Documentation & final validation | 30-45 min |

**Total Estimated Time**: 2.5-3.5 hours

---

## 📋 User Story Mapping

### User Story 1 (P1): Aplicar Tema Oscuro Permanente 🎯 MVP
- **Tasks**: T010-T015
- **Goal**: App muestra siempre tema oscuro, independiente del SO
- **Files Modified**:
  - `main.py` (add theme setup)
  - `wifi_connector/gui/main_window.py` (verify CTk widgets)
  - `wifi_connector/gui/about.py` (verify CTk widgets)
- **Independent Test**: Launch app on light OS → verify dark theme

### User Story 2 (P2): Contraste y Legibilidad
- **Tasks**: T016-T023
- **Goal**: Todos los elementos legibles con contraste WCAG AA 4.5:1
- **Files Modified**: None (validation only)
- **Independent Test**: Navigate all screens + measure contrast with tools

---

## ⚡ Parallelization Opportunities

### Phase 1 (Setup): 2 parallel tasks
```bash
# Developer A
T001: Check customTkinter >= 5.0.0 in requirements.txt

# Developer B  
T002: Audit GUI for legacy widgets (grep search)
```

### Phase 2 (Foundational): 3 constants in parallel
```bash
# After T003 creates theme.py:

# Developer A
T004: Add APPEARANCE_MODE = "dark"

# Developer B
T005: Add COLOR_THEME = "blue"

# Developer C
T006: Add THEME_SETUP_MAX_TIME_MS = 100
```

### Phase 4 (User Story 2): 2 visual audits in parallel
```bash
# Developer A
T016: Visual audit main window

# Developer B
T017: Visual audit about window
```

### Phase 5 (Polish): 7 parallel tasks
```bash
# All developers can work simultaneously on:
T024-T027: Documentation (4 sections of gui/README.md)
T029: Update requirements.txt
T030: Performance benchmark
T031: Log review
```

---

## 🎯 MVP Strategy

### Minimum Viable Product (MVP)
**Scope**: User Story 1 (P1) ONLY
- **Tasks**: T001-T015 (Setup + Foundational + US1)
- **Time**: ~75-90 minutes
- **Deliverable**: App launches with dark theme always

This delivers the core request: "tema sea siempre oscuro indistintamente del sistema"

### Incremental Delivery Plan

**Sprint 1** (MVP): Setup + Foundational + User Story 1
- T001-T015
- Result: Working dark theme
- Time: 75-90 minutes

**Sprint 2**: User Story 2 (Contrast Validation)
- T016-T023
- Result: Verified WCAG AA compliance
- Time: 60-90 minutes

**Sprint 3**: Polish
- T024-T031
- Result: Documented & fully validated
- Time: 30-45 minutes

---

## 📊 Task Format Validation

All 31 tasks follow the required checklist format:

✅ **Checkbox**: All tasks start with `- [ ]`  
✅ **Task ID**: Sequential (T001-T031)  
✅ **[P] marker**: Present on parallelizable tasks (T004, T005, T006, T013, T014, T016, T017, T024, T025, T026, T027, T029, T030, T031)  
✅ **[Story] label**: Present on user story tasks ([US1] for T010-T015, [US2] for T016-T023)  
✅ **File paths**: Included in all implementation tasks  

**Example**:
```markdown
- [ ] T010 [US1] Modify main.py to import setup_dark_theme from wifi_connector.utils.theme
- [ ] T004 [P] Define APPEARANCE_MODE constant = "dark" in wifi_connector/utils/theme.py
```

---

## 📦 Deliverables Structure

### Files Created
- `wifi_connector/utils/theme.py` (NEW - T003-T009)
- `wifi_connector/gui/README.md` (NEW - T024-T027)

### Files Modified
- `main.py` (T010-T012)
- `wifi_connector/gui/main_window.py` (T013 - verification/migration)
- `wifi_connector/gui/about.py` (T014 - verification/migration)
- `requirements.txt` (T029 - pin customTkinter version)

### Total LOC Impact
- **New**: ~150 lines (theme.py ~40, README.md ~110)
- **Modified**: ~10 lines (main.py ~5, optional GUI adjustments ~5)
- **Total**: ~160 lines

---

## 🧪 Testing Strategy

### Manual Testing (Primary)
**Why**: No automated tests requested in spec.md

**User Story 1 Tests**:
1. Launch app on light theme OS → verify dark (T015)
2. Change OS theme while running → verify app stays dark
3. Restart app → verify dark theme persists
4. Open all windows → verify consistent dark theme

**User Story 2 Tests**:
1. Visual audit all controls for legibility (T016-T017)
2. Test interaction states visibility (T018-T020)
3. Measure contrast ratios with tools (T021-T022)
4. Fix any insufficient contrast (T023)

**Tools**:
- WebAIM Contrast Checker
- Color Contrast Analyzer
- quickstart.md validation guide (15-20 min)

### Automated Testing (Optional Future Enhancement)
If later adding test coverage:
- Unit tests: `tests/test_theme.py` (constants, setup function)
- Integration tests: `tests/integration/test_theme_coverage.py` (all windows dark)

---

## 📐 Dependencies Graph

```
Phase 1 (Setup)
├── T001 ─┐
└── T002 ─┴─> Phase 2 (Foundational)
            ├── T003 ─┬─> T004
            │         ├─> T005  
            │         └─> T006 ─┬─> T007 ─┬─> T008
            │                   │         └─> T009
            │                   │
            └─────────────────────> Phase 3 (US1)
                                  ├── T010
                                  ├── T011
                                  ├── T012
                                  ├── T013 ──┐
                                  ├── T014 ──┴─> T015
                                  │
                                  └─> Phase 4 (US2)
                                      ├── T016 ──┐
                                      ├── T017 ──┴─> T018 ─> T019 ─> T020
                                      │                              │
                                      └──────────────────────────────┴─> T021 ─> T022 ─> T023
                                                                          │
                                                                          └─> Phase 5 (Polish)
                                                                              ├── T024 ──┐
                                                                              ├── T025 ──┤
                                                                              ├── T026 ──┼─> T028
                                                                              ├── T027 ──┤
                                                                              ├── T029 ──┤
                                                                              ├── T030 ──┤
                                                                              └── T031 ──┘
```

---

## ✅ Success Criteria Mapping

Each Success Criterion from spec.md is validated by specific tasks:

| Success Criterion | Validating Tasks | How Verified |
|-------------------|------------------|--------------|
| **SC-001**: <100ms performance | T030 | Performance benchmark per quickstart.md |
| **SC-002**: 100% coverage | T015, T016-T017 | Visual verification all windows dark |
| **SC-003**: WCAG AA 4.5:1 contrast | T021-T022 | Contrast checker tool measurements |
| **SC-004**: User comfort | Post-implementation | User feedback (out of scope for tasks) |

---

## 🚀 Implementation Readiness

### Pre-Implementation Checklist ✅
- [x] Specification complete (spec.md)
- [x] Design complete (plan.md, research.md, data-model.md, contracts/)
- [x] Requirements validated (checklists/pre-implementation.md)
- [x] Gaps resolved (3 critical gaps fixed in spec.md)
- [x] Constitution check passed
- [x] Task list generated (tasks.md)

### Ready to Start
```bash
# Begin implementation immediately:
git checkout 001-dark-theme-mode

# Start with Setup phase:
# T001: Verify customTkinter >= 5.0.0 in requirements.txt
# T002: Audit GUI for legacy widgets
```

---

## 📝 Notes & Recommendations

### Key Decisions Made
1. **No automated tests**: Spec doesn't request TDD → manual validation sufficient
2. **Fail-fast strategy**: If theme fails, app exits (FR-007)
3. **No persistence**: Theme is hardcoded, no config file
4. **Manual contrast validation**: WCAG tools instead of programmatic checks

### Risk Mitigations
- **Legacy widgets**: T002 audits early, allows planning for migration if needed
- **Version pinning**: T001 verifies customTkinter >= 5.0.0
- **Logging**: T008-T009 ensure debugging capability
- **Visual validation**: T016-T023 ensure UX quality

### Future Enhancements (Out of Scope)
- Configurable themes (light/dark/system)
- Animated transitions
- Custom color palettes
- Automated contrast tests

---

## 📞 Next Actions

### Immediate (Start Implementation)
1. ✅ Read tasks.md fully
2. ✅ Checkout branch `001-dark-theme-mode`
3. ✅ Begin Phase 1 (T001-T002)
4. ✅ Proceed sequentially through phases

### During Implementation
- Mark tasks as `[x]` when completed
- Commit incrementally (after each phase)
- Reference task IDs in commit messages: `git commit -m "[T010] Add theme setup to main.py"`

### After Implementation
- Run quickstart.md validation (T028)
- Verify all acceptance criteria (see tasks.md §Acceptance Checklist)
- Create PR with reference to spec.md
- Request review focusing on US1 and US2 scenarios

---

**Status**: ✅ **READY FOR IMPLEMENTATION**  
**Estimated Completion**: 2.5-3.5 hours  
**MVP Delivery**: 75-90 minutes (User Story 1 only)

**Start Command**: `git checkout 001-dark-theme-mode && code specs/001-dark-theme-mode/tasks.md`
