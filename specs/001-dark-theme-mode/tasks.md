# Tasks: Tema Oscuro Forzado

**Input**: Design documents from `/specs/001-dark-theme-mode/`  
**Branch**: `001-dark-theme-mode`  
**Created**: 2025-12-13

**Prerequisites**: 
- ✅ plan.md (complete)
- ✅ spec.md (2 user stories: P1, P2)
- ✅ research.md (complete)
- ✅ data-model.md (complete)
- ✅ contracts/theme-api.md (complete)

**Tests**: No tests explicitly requested in specification. Implementation will focus on working code + manual validation per quickstart.md.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[US1]**: User Story 1 - Aplicar Tema Oscuro Permanente (P1)
- **[US2]**: User Story 2 - Contraste y Legibilidad en Tema Oscuro (P2)
- Include exact file paths in descriptions

**Path Convention**: Single project with `wifi_connector/` package at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify dependencies and audit existing GUI code

- [X] T001 Verify customTkinter >= 5.0.0 installed in requirements.txt
- [X] T002 Audit GUI code for tkinter legacy widgets using grep (search for `import tkinter as tk` and `tk.` usage in wifi_connector/gui/)

**Checkpoint**: Dependencies verified, legacy widgets identified (if any)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core theme infrastructure that MUST exist before any GUI modifications

**⚠️ CRITICAL**: No user story work can begin until theme module exists

- [X] T003 Create wifi_connector/utils/theme.py module with imports (customtkinter, logger)
- [X] T004 [P] Define APPEARANCE_MODE constant = "dark" in wifi_connector/utils/theme.py
- [X] T005 [P] Define COLOR_THEME constant = "blue" in wifi_connector/utils/theme.py
- [X] T006 [P] Define THEME_SETUP_MAX_TIME_MS constant = 100 in wifi_connector/utils/theme.py
- [X] T007 Implement setup_dark_theme() function in wifi_connector/utils/theme.py with try-except error handling
- [X] T008 Add logging for successful theme configuration in setup_dark_theme() using wifi_connector.utils.logger
- [X] T009 Add logging for errors (ImportError, AttributeError, RuntimeError) in setup_dark_theme()

**Checkpoint**: Theme module complete and ready to be called from main.py

---

## Phase 3: User Story 1 - Aplicar Tema Oscuro Permanente (Priority: P1) 🎯 MVP

**Goal**: La aplicación muestra siempre un tema oscuro al iniciar, independientemente de la configuración del sistema operativo, y lo mantiene durante toda la sesión.

**Independent Test**: Iniciar aplicación en sistema con tema claro → verificar que app muestra tema oscuro. Cambiar tema del SO mientras app corre → verificar que app mantiene tema oscuro.

### Implementation for User Story 1

- [X] T010 [US1] Modify main.py to import setup_dark_theme from wifi_connector.utils.theme
- [X] T011 [US1] Call setup_dark_theme() in main.py BEFORE importing GUI modules (main_window, about)
- [X] T012 [US1] Add try-except in main.py to catch theme setup failures and exit with sys.exit(1) per FR-007 (fail-fast strategy)
- [X] T013 [US1] Verify main_window.py uses customTkinter widgets (CTkButton, CTkEntry, CTkLabel) - migrate if needed
- [X] T014 [US1] Verify about.py uses customTkinter widgets - migrate if needed
- [X] T015 [US1] Test manual: Launch app on system with light theme → verify dark theme applied

**Checkpoint**: At this point, User Story 1 (P1) is complete - app launches with dark theme and maintains it during session

---

## Phase 4: User Story 2 - Contraste y Legibilidad en Tema Oscuro (Priority: P2)

**Goal**: Todos los elementos de la interfaz (texto, botones, campos de entrada, mensajes de estado) son claramente legibles en tema oscuro con contraste WCAG AA 4.5:1.

**Independent Test**: Navegar por todas las pantallas de la aplicación, probar estados hover/focus/disabled en controles, y verificar que todos los textos son legibles usando herramientas de contraste.

### Implementation for User Story 2

- [X] T016 [P] [US2] Visual audit: Open main window and verify all text elements are legible
- [X] T017 [P] [US2] Visual audit: Open about window and verify all text elements are legible
- [X] T018 [US2] Test hover state: Hover over buttons and verify visual change is perceptible
- [X] T019 [US2] Test focus state: Tab through interactive elements and verify focus indicators are visible
- [X] T020 [US2] Test disabled state: Disable controls programmatically and verify disabled state is distinguishable
- [X] T021 [US2] Use contrast checker tool on main window text (WebAIM or Color Contrast Analyzer)
- [X] T022 [US2] Document contrast ratios found for critical text elements (target: ≥ 4.5:1)
- [X] T023 [US2] If any widgets have insufficient contrast, identify and fix (adjust colors or migrate widget type)

**Checkpoint**: At this point, User Stories 1 AND 2 are complete - all GUI elements are legible with sufficient contrast

---

## Phase 5: Documentation & Polish

**Purpose**: Document dark theme patterns and create validation guide for future GUI changes

- [X] T024 [P] Create wifi_connector/gui/README.md documenting dark theme usage patterns
- [X] T025 [P] Document in gui/README.md that theme is hardcoded (no config file, always dark)
- [X] T026 [P] Document in gui/README.md how to add new windows (must use customTkinter widgets)
- [X] T027 [P] Add section in gui/README.md about contrast requirements (WCAG AA 4.5:1)
- [X] T028 Run complete validation per quickstart.md (15-20 minutes)
- [X] T029 Update requirements.txt with explicit customTkinter >= 5.0.0 if not already pinned
- [X] T030 [P] Performance check: Verify theme application completes in <100ms using quickstart.md benchmarks
- [X] T031 Review all log outputs for theme-related messages (should see "Dark theme configured successfully")

**Checkpoint**: Feature fully documented and validated per quickstart.md acceptance checklist

---

## Phase 6: Automated Tests

**Purpose**: Create automated test suite for theme functionality to ensure regression protection

- [X] T032 [P] Create tests/test_theme.py with unit tests for setup_dark_theme() function
- [X] T033 [P] Add tests in test_theme.py for theme constants (APPEARANCE_MODE, COLOR_THEME)
- [X] T034 Create tests/integration/test_theme_coverage.py to verify all windows apply dark theme
- [X] T035 Update tests/test_gui.py to include theme application verification in existing GUI tests

**Checkpoint**: All tests pass, providing automated regression protection for dark theme feature

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (T001-T002) - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (T003-T009) - Core theme application
- **User Story 2 (Phase 4)**: Depends on User Story 1 (T010-T015) - Validates legibility of applied theme
- **Polish (Phase 5)**: Depends on all user stories (T010-T023) being complete
- **Automated Tests (Phase 6)**: Depends on Polish (T024-T031) - Tests require fully implemented feature

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) completes - No dependencies on other stories
- **User Story 2 (P2)**: Depends on User Story 1 being implemented first (need applied theme to verify contrast)

### Within Each Phase

**Phase 1 (Setup)**:
- T001 and T002 can run in parallel (independent verification steps)

**Phase 2 (Foundational)**:
- T003 must complete first (create file)
- T004, T005, T006 can run in parallel after T003 (add constants to same file)
- T007 must wait for T004, T005, T006 (implement function using constants)
- T008, T009 can run in parallel after T007 (add logging to function)

**Phase 3 (User Story 1)**:
- T010-T012 must be sequential (modify main.py in specific order)
- T013 and T014 can run in parallel (audit different files)
- T015 must be last (manual test after implementation)

**Phase 4 (User Story 2)**:
- T016, T017 can run in parallel (visual audits of different windows)
- T018, T019, T020 must be sequential (testing different states)
- T021, T022, T023 must be sequential (measure → document → fix)

**Phase 5 (Polish)**:
- T024, T025, T026, T027 can run in parallel (writing different sections of README.md)
- T028 must wait for all implementation tasks (runs quickstart validation)
- T029, T030, T031 can run in parallel after T028

**Phase 6 (Automated Tests)**:
- T032, T033 can run in parallel (both edit test_theme.py)
- T034 can run in parallel with T032-T033 (creates new file)
- T035 must be last (modifies existing test_gui.py after understanding theme tests)

### Parallel Opportunities

**Setup Phase**: Both tasks (T001, T002) can run in parallel  
**Foundational Phase**: Constants (T004, T005, T006) can be added in parallel  
**User Story 1**: Widget audits (T013, T014) can run in parallel  
**User Story 2**: Visual audits (T016, T017) can run in parallel  
**Polish Phase**: Documentation (T024-T027) and final checks (T029-T031) have parallelization opportunities  
**Automated Tests Phase**: Test creation tasks (T032-T034) can run in parallel

---

## Parallel Example: Foundational Phase

Once T003 creates the theme.py file, three developers can work simultaneously:

```bash
# Developer A: Add APPEARANCE_MODE constant
# wifi_connector/utils/theme.py
APPEARANCE_MODE: Literal["dark"] = "dark"

# Developer B: Add COLOR_THEME constant  
# wifi_connector/utils/theme.py
COLOR_THEME: Literal["blue"] = "blue"

# Developer C: Add THEME_SETUP_MAX_TIME_MS constant
# wifi_connector/utils/theme.py
THEME_SETUP_MAX_TIME_MS: int = 100
```

After merge, one developer implements T007-T009 (function + logging).

---

## Parallel Example: User Story 2 Visual Audits

Two developers can audit different windows simultaneously:

```bash
# Developer A: Audit main window (T016)
python main.py
# → Open main window
# → Check all text is legible
# → Document findings

# Developer B: Audit about window (T017)  
python main.py
# → Open Help → About
# → Check all text is legible
# → Document findings
```

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**User Story 1 (P1) ONLY** constitutes the MVP:
- Theme module created (T003-T009)
- Theme applied at app startup (T010-T012)
- Basic verification (T015)

This delivers the core feature: "tema sea siempre oscuro indistintamente del sistema"

### Incremental Delivery

1. **Sprint 1**: Setup + Foundational + User Story 1 (T001-T015) → MVP ready
2. **Sprint 2**: User Story 2 (T016-T023) → Contrast validation complete
3. **Sprint 3**: Polish (T024-T031) → Documentation and final validation
4. **Sprint 4**: Automated Tests (T032-T035) → Regression protection

**Estimated Time**:
- Setup + Foundational: 30 minutes
- User Story 1: 45-60 minutes
- User Story 2: 60-90 minutes (includes manual testing with tools)
- Polish: 30-45 minutes
- Automated Tests: 45-60 minutes

**Total: 3.5-4.5 hours** (updated from 2.5-3.5h to include automated tests)

---

## Testing Strategy

### Automated Testing (Phase 6)

**Unit Tests (test_theme.py)**:
- Test setup_dark_theme() function execution
- Test theme constants (APPEARANCE_MODE, COLOR_THEME, THEME_SETUP_MAX_TIME_MS)
- Test error handling in theme setup
- Mock customtkinter.set_appearance_mode() and verify calls

**Integration Tests (test_theme_coverage.py)**:
- Verify all windows (main_window, about) inherit dark theme
- Test theme persistence across window lifecycle
- Verify no tkinter legacy widgets present

**GUI Tests (test_gui.py updates)**:
- Add theme verification to existing GUI tests
- Ensure all GUI tests run with dark theme active

### Manual Testing (Required)

**User Story 1 Validation**:
- Scenario 1: Launch app on light theme OS → verify dark theme
- Scenario 2: Change OS theme while app running → verify app stays dark
- Scenario 3: Restart app → verify dark theme persists
- Scenario 4: Open all windows (main, about) → verify consistent dark theme

**User Story 2 Validation**:
- Scenario 1: Verify all controls (buttons, fields, labels) are legible
- Scenario 2: Test message colors (success, error, warning) if applicable
- Scenario 3: Test interaction states (hover, focus, disabled) visibility
- Scenario 4: Test text input fields for visibility

**Contrast Validation Tools**:
- WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
- Color Contrast Analyzer (desktop app)
- Screenshot critical text and verify ratio ≥ 4.5:1

**Performance Validation**:
- Measure app startup time (should be instantaneous, theme <100ms)
- Check logs for "Dark theme configured successfully" message

---

## Success Criteria Mapping

**SC-001** (Performance): Verified by T030 (benchmark <100ms)  
**SC-002** (100% Coverage): Verified by T015 (US1), T016-T017 (US2 visual audits)  
**SC-003** (Contrast WCAG AA): Verified by T021-T022 (contrast tool measurements)  
**SC-004** (User Comfort): Post-implementation feedback (out of scope for tasks)

---

## Acceptance Checklist

Before marking feature complete, verify:

- [x] User Story 1: App launches with dark theme regardless of OS setting
- [x] User Story 1: Theme persists during entire session
- [x] User Story 1: Theme persists across app restarts
- [x] User Story 1: All windows show consistent dark theme
- [x] User Story 2: All text elements are legible
- [x] User Story 2: Message states are distinguishable
- [x] User Story 2: Interaction states are perceptible
- [x] User Story 2: Text fields show clear text input
- [x] FR-001: Dark theme applied at startup
- [x] FR-002: Theme maintained during session
- [x] FR-003: All windows use dark theme
- [x] FR-004: Contrast meets WCAG AA 4.5:1
- [x] FR-005: States have consistent colors
- [x] FR-006: Errors logged appropriately
- [x] FR-007: App exits if theme setup fails
- [x] SC-001: Theme applies in <100ms
- [x] SC-002: 100% of windows dark
- [x] SC-003: All text meets 4.5:1 contrast
- [x] quickstart.md validation complete (15-20 min)

---

## Notes

- **No automated tests** because spec doesn't request them (Out of Scope section doesn't mention TDD)
- **Manual validation** per quickstart.md is sufficient for this feature
- **Widgets legacy**: If T002 finds `tk.*` widgets, add migration tasks to Phase 2
- **Performance**: customTkinter's `set_appearance_mode()` is <1ms per research.md
- **Fail-fast**: If theme setup fails, app exits immediately (FR-007)
- **No persistence**: Theme is hardcoded, no config file (per clarifications)
- **Documentation**: gui/README.md created in Phase 5 for future developers

**Ready for Implementation**: All tasks defined, dependencies mapped, parallel opportunities identified.
