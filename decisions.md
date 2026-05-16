# Design Decisions

> Records notable design choices and their rationale.
> Add new entries at the top.

---

## 2026-05-16: Obsidian-compatible documentation system

- **Decision**: Install a modular documentation system with hub-and-spoke architecture, migrating content from the monolithic AGENTS.md into focused docs.
- **Why**: AGENTS.md was 47KB — too large for a single AI context window. Modular docs let agents load only what they need. Wiki links enable Obsidian graph navigation.
- **Impact**: All AGENTS.md content is preserved across 10 focused docs. AGENTS.md removed after verification (Phase 4).

## 2026-03-15: 8.2 MB target size (not 10 MB)

- **Decision**: Target output is 8.2 MB, not the full 10 MB Discord Free Tier limit.
- **Why**: Bitrate calculations are approximate because FFmpeg uses variable bitrate encoding. A safety margin prevents output from exceeding the 10 MB hard limit. 8.2 MB was chosen as a practical balance between quality and reliability.
- **Impact**: Anyone tuning `TARGET_FILESIZE_MB` should not exceed ~9.0 MB without accepting risk of Discord rejection.

## 2026-03-15: Single-file architecture (app.py)

- **Decision**: All GUI, CLI, and compression logic lives in a single 282-line Python file.
- **Why**: The application is small enough that a single file is simpler than a package structure. Reduces packaging complexity for PyInstaller. No module imports to manage.
- **Impact**: The file has some code duplication (CLI mode duplicates the progress popup). This is an accepted tradeoff for simplicity.

## 2026-03-15: Tkinter over Qt or web frameworks

- **Decision**: Use Tkinter (Python built-in) for the GUI.
- **Why**: Tkinter requires no external dependencies. The GUI is simple (file pickers, buttons, progress bar). No need for the complexity of Qt or a web stack.
- **Impact**: UI styling is limited to Tkinter's capabilities. Cross-platform look-and-feel varies.

---

Related: [[CLAUDE]] | [[docs/_index]]
