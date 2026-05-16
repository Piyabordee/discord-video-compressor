# Video Compressor (~9MB) — Project Hub

> Central operational hub for AI agents working on this codebase.
> Full documentation: [[docs/_index]].
> Stable rules: `./.claude/rules/`.

---

## Identity

| Field | Value |
|-------|-------|
| Name | Video Compressor to ~9MB |
| Type | Desktop utility (Windows) |
| Stack | Python 3.8+, Tkinter, FFmpeg, PyInstaller |
| Version | 1.0.0 |
| License | MIT |

---

## Read First

- `./.claude/rules/*` — stable rules (always apply)
- `docs/_index.md` [[docs/_index]] — full documentation map
- `docs/project/overview.md` [[docs/project/overview]] — project identity and context
- `README.md` [[README]] — user-facing introduction

---

## Task Routing

| Task | Read First |
|------|------------|
| Modifying compression / bitrate logic | `docs/features/compression-workflow.md` |
| Adding or modifying UI strings (Thai) | `docs/reference/thai-glossary.md` |
| Changing FFmpeg commands or path discovery | `docs/integrations/ffmpeg.md` |
| Build, packaging, or release | `docs/build/build-and-release.md` |
| Shell extension / context menu | `docs/integrations/shell-extension.md` |
| Writing tests | `docs/testing/testing-strategy.md` |
| Tuning constants or Discord limits | `docs/reference/constants.md` |
| Adding new entry mode or CLI behavior | `docs/features/entry-modes.md` |

---

## Directory Tree (Authoritative)

```text
discord-video-compressor/
├── .claude/rules/               # Stable rules (coding style, Thai language)
├── docs/
│   ├── _index.md                # Documentation navigation hub
│   ├── project/
│   │   └── overview.md          # Project identity and context
│   ├── architecture/
│   │   └── structure.md         # App structure and subsystem map
│   ├── features/
│   │   ├── compression-workflow.md  # Core compression feature
│   │   └── entry-modes.md       # GUI, CLI, context menu modes
│   ├── integrations/
│   │   ├── ffmpeg.md            # FFmpeg usage and parameters
│   │   └── shell-extension.md   # Windows COM shell extension
│   ├── build/
│   │   └── build-and-release.md # Build chain and release process
│   ├── testing/
│   │   └── testing-strategy.md  # Testing framework and test cases
│   └── reference/
│       ├── constants.md         # Tunable constants and Discord limits
│       └── thai-glossary.md     # Thai-English UI string reference
├── app.py                       # Main application (GUI + CLI + logic)
├── VideoCompressor9MB.spec      # PyInstaller build config
├── setup_compress9mb.iss        # Inno Setup installer script
├── shell_extension/             # Windows COM shell extension (C++)
├── CLAUDE.md                    # This file
├── decisions.md                 # Design decisions log
├── README.md                    # User-facing documentation
└── LICENSE                      # MIT License
```

---

## Quick Commands

```bash
python app.py                              # run GUI mode
python app.py "path/to/video.mp4"          # run CLI mode
pyinstaller VideoCompressor9MB.spec        # build executable
```

---

## Working Rules

1. **Thai-only UI** — all user-facing strings are in Thai; check [[docs/reference/thai-glossary]] before adding or modifying text
2. **FFmpeg is external** — never assume FFmpeg is installed; always handle the "not found" path
3. **app.py is a monolith** — keep changes surgical; do not refactor beyond task scope
4. **Target output ~8.2 MB** — safety margin under Discord's 10 MB Free Tier limit; see [[docs/reference/constants]]

---

## Doc Workflow

When creating or significantly modifying a feature:

1. Create or update the feature doc in `docs/features/` (or appropriate category)
2. Add wiki links in the doc's Related section
3. Add entry to the Documentation Map below
4. Update `docs/_index.md` if a new doc was created
5. Update `decisions.md` if a design choice was made

### Where to put docs

| Category | Path | When |
|----------|------|------|
| Feature workflow | `docs/features/` | New user-facing behavior |
| Architecture | `docs/architecture/` | Structural changes |
| Reference | `docs/reference/` | New constants, config options |
| Build/release | `docs/build/` | Build process changes |
| Integration | `docs/integrations/` | External tool changes |

---

## Documentation Map

### Project
- [[docs/project/overview]] — purpose, users, tech stack, resources

### Architecture
- [[docs/architecture/structure]] — app structure, subsystem map, component interaction

### Features
- [[docs/features/compression-workflow]] — bitrate calculation, FFmpeg execution, progress tracking, troubleshooting
- [[docs/features/entry-modes]] — GUI, CLI, and right-click context menu modes

### Integrations
- [[docs/integrations/ffmpeg]] — FFmpeg/FFprobe path discovery, commands, parameters, troubleshooting
- [[docs/integrations/shell-extension]] — Windows COM shell extension, build, install, registry

### Build
- [[docs/build/build-and-release]] — PyInstaller, Inno Setup, release checklist, versioning

### Testing
- [[docs/testing/testing-strategy]] — framework, test cases, CI/CD

### Reference
- [[docs/reference/constants]] — tunable constants, impact analysis, Discord limits
- [[docs/reference/thai-glossary]] — Thai-English UI string reference table

---

## Key Warnings

- **Thai-only UI** — see [[docs/reference/thai-glossary]]
- **FFmpeg required but not in repo** — see [[docs/integrations/ffmpeg]]
- **Bitrate formula is approximate** — output may vary; see [[docs/reference/constants]]
- **app.py duplicates CLI progress popup** — potential refactoring target

---

## Definition of Done

- [ ] Change implemented with minimal scope
- [ ] Related docs updated when behavior changed
- [ ] Commit is scoped to one issue/change set
- [ ] `decisions.md` updated for lasting design choices
- [ ] CLAUDE.md updated to match current project state

---

## Session Closeout

At the end of each work session:

1. Update `CLAUDE.md` to match current project state
2. Update `decisions.md` with new stable decisions
3. Re-check Documentation Map and links

---

## Related

- [[docs/_index]] — documentation navigation
- [[README]] — user-facing intro
- `./.claude/rules/` — stable rules
- [[decisions]] — design decisions log
