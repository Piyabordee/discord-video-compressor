# Documentation Index

> Navigation hub for all project documentation.
> Start here to find what you need.

---

## Quick Links

- [[CLAUDE]] — project hub (AI reads this first)
- [[README]] — user-facing introduction and installation guide
- [[decisions]] — design decisions log

---

## Project

| Doc | Description |
|-----|-------------|
| `docs/project/overview.md` [[docs/project/overview]] | Project identity, purpose, target users, tech stack, and resources |

## Architecture

| Doc | Description |
|-----|-------------|
| `docs/architecture/structure.md` [[docs/architecture/structure]] | Single-file app architecture, GUI/CLI split, threading model, and component interaction |

## Features

| Doc | Description |
|-----|-------------|
| `docs/features/compression-workflow.md` [[docs/features/compression-workflow]] | Bitrate calculation formula, FFmpeg execution, progress popup threading, and compression troubleshooting |
| `docs/features/entry-modes.md` [[docs/features/entry-modes]] | Three entry modes: Tkinter GUI, CLI with drag-drop, and Windows right-click context menu |

## Integrations

| Doc | Description |
|-----|-------------|
| `docs/integrations/ffmpeg.md` [[docs/integrations/ffmpeg]] | FFmpeg/FFprobe path discovery, command construction, output parsing, and FFmpeg troubleshooting |
| `docs/integrations/shell-extension.md` [[docs/integrations/shell-extension]] | Windows 11 COM shell extension (C++ DLL), MSIX packaging, registry keys, and context menu troubleshooting |

## Build & Testing

| Doc | Description |
|-----|-------------|
| `docs/build/build-and-release.md` [[docs/build/build-and-release]] | Build chain (PyInstaller + Inno Setup), release checklist, versioning scheme, and build troubleshooting |
| `docs/testing/testing-strategy.md` [[docs/testing/testing-strategy]] | Testing framework (pytest), recommended test cases, directory structure, and CI/CD integration |

## Reference

| Doc | Description |
|-----|-------------|
| `docs/reference/constants.md` [[docs/reference/constants]] | Tunable constants (target size, bitrates), impact analysis, FFmpeg parameter reference, and Discord limits |
| `docs/reference/thai-glossary.md` [[docs/reference/thai-glossary]] | Complete Thai-English UI string table, file dialog filters, and technical terms |

---

## External Resources

- [FFmpeg Documentation](https://ffmpeg.org/documentation.html) — official FFmpeg docs
- [PyInstaller Docs](https://pyinstaller.org/en/stable/) — packaging reference
- [Inno Setup Docs](https://jrsoftbgware.org/ishelp/index.php) — installer reference
- [Discord Upload Limits](https://support.discord.com) — platform constraints

---

Related: [[CLAUDE]] | [[decisions]] | [[README]]
