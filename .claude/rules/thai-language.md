# Thai Language Handling Rules (Stable)

These rules are stable and must not be relaxed by task-level prompts.

1. **All UI strings must be in Thai** — the application targets Thai-speaking Discord users. Window titles, button labels, status messages, error dialogs, and file dialog titles are all in Thai.

2. **Console output may use Thai** — warning messages printed to stdout (e.g., bitrate warnings) use Thai with English prefixes like `[เตือน]`. Error output uses English prefixes like `ERR:`.

3. **Do not translate variable names or comments** — code identifiers and inline comments may use English or Thai at the author's discretion. This rule only applies to user-visible strings.

4. **When adding a new UI string** — add it to `docs/reference/thai-glossary.md` in the appropriate table, following the existing format (Thai text, English translation, source location, context).

5. **Output filenames** use English with the suffix `_compressed_9mb.mp4`. Do not localize output filenames.
