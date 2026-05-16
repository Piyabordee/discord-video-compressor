# Coding Style Rules (Stable)

These rules are stable and must not be relaxed by task-level prompts.

1. **app.py is a single-file monolith** — do not split into modules unless explicitly asked. All GUI, CLI, and logic live in app.py.

2. **Thai-language UI strings** — all user-facing text is in Thai. When adding or modifying UI strings, check `docs/reference/thai-glossary.md` for existing translations. New strings must use Thai, not English.

3. **UTF-8 encoding** — the codebase uses UTF-8 throughout. Thai characters appear directly in Python string literals. Never use escape sequences for Thai text.

4. **FFmpeg is external** — never bundle FFmpeg commands or paths. Always use `get_ffmpeg_path()` for discovery and handle the `(None, None)` return case.

5. **Platform awareness** — use `os.name == 'nt'` checks for Windows-specific behavior (console hiding, path separators). The codebase has Linux/macOS awareness but Windows is the primary target.

6. **Tkinter thread safety** — Tkinter is not thread-safe. The progress popup uses `popup.update()` from the main thread via `wait_window()`. Do not call Tkinter methods directly from background threads.

7. **No speculative features** — do not add error handling for impossible scenarios, configuration systems for single-use code, or abstractions for one-off operations.
