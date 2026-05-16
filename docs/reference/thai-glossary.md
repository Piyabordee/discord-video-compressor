# Thai-English Glossary

> Complete reference of Thai-language UI strings in the application.

---

## Overview

The application's UI is entirely in Thai, targeting Thai-speaking Discord users. This glossary maps every Thai string to its English translation, source location, and usage context. Use this when adding, modifying, or translating UI text.

## Context Snapshot

- All user-facing strings are Thai
- Code uses UTF-8 with Thai characters directly in string literals (no escape sequences)
- Console output uses a mix: Thai warnings with English prefixes (`ERR:`, `OK:`)
- Output filenames use English (`_compressed_9mb.mp4`)

## When to Read This

### Trigger

- Adding a new UI string or modifying an existing one
- Translating the application to another language
- Understanding what a Thai error message means
- Building i18n support

### Read With

- `docs/features/entry-modes.md` [[docs/features/entry-modes]] — where UI strings appear in the user journey
- `docs/architecture/structure.md` [[docs/architecture/structure]] — code structure for locating strings

## UI Strings

Strings listed in order of appearance in code (`app.py`).

| Thai | English | Line | Context |
|:-----|:--------|:-----|:--------|
| โปรแกรมบีบอัดวิดีโอ (~9MB) | Video Compressor (~9MB) | 125 | Window title |
| ไฟล์วิดีโอต้นฉบับ: | Original video file: | 132 | Label |
| เลือกไฟล์ | Select file | 134 | Button |
| ไฟล์วิดีโอผลลัพธ์: | Output video file: | 135 | Label |
| เลือกที่จัดเก็บ | Select save location | 137 | Button |
| เริ่มบีบอัดให้ได้ ~9MB | Start compress to ~9MB | 138 | Main button |
| สถานะ: พร้อมทำงาน | Status: Ready | 139 | Status label |
| สถานะ: กำลังบีบอัด... | Status: Compressing... | 160 | During compression |
| เสร็จสิ้น: {mb:.2f} MB | Completed: {mb:.2f} MB | 174 | Success message |
| ยกเลิกการบีบอัด | Compression cancelled | 176 | Cancel status |
| กำลังบีบอัด… | Compressing… | 64, 204 | Progress popup title |
| ยกเลิก | Cancel | 76, 216 | Cancel button |
| ข้อมูลไม่ครบ | Incomplete information | 159 | Warning title |
| กรุณาเลือกไฟล์ต้นฉบับและผลลัพธ์ | Please select input and output files | 159 | Warning message |
| ไม่พบ FFmpeg/ffprobe | FFmpeg/ffprobe not found | 129, 187 | Error message |
| FFmpeg ผิดพลาด | FFmpeg error | 178 | FFmpeg error title |
| ผิดพลาด | Error occurred | 180 | Generic error title |
| วิดีโอยาวเกินไปสำหรับงบขนาดไฟล์/เสียงปัจจุบัน | Video too long for current file size/audio budget | 47, 166 | Runtime error |
| [เตือน] บิตเรตวิดีโอต่ำมาก: {v_kbps:.2f} kbps | [Warning] Very low video bitrate: {v_kbps:.2f} kbps | 49, 168 | Console warning |
| เลือกไฟล์วิดีโอ | Select video file | 143 | File dialog title |
| ตำแหน่งผลลัพธ์ | Output location | 152 | Save dialog title |
| บีบอัดสำเร็จ | Compression successful | 267 | Success dialog title |
| OK | OK | 174, 267 | Success dialog button |
| OK: {out} ({mb:.2f} MB) | OK: {out} ({mb:.2f} MB) | 264 | CLI success output |
| ERR: {e} | ERROR: {e} | 274 | CLI error output |
| Error | Error | 129, 180 | Error dialog title |

## File Dialog Filters

| Thai | English | Used For |
|:-----|:--------|:---------|
| Video | Video files | File type filter (open dialog) |
| All | All files | File type filter (open dialog) |
| MP4 | MP4 files | File type filter (save dialog) |

## Technical Terms (Thai in code)

| Thai | English | Notes |
|:-----|:--------|:-------|
| บีบอัด | Compress | Verb: to compress |
| วิดีโอต้นฉบับ | Original video / Source video | Input file |
| วิดีโอผลลัพธ์ | Output video | Compressed file |
| บิตเรต | Bitrate | Video/audio data rate |
| เลือกไฟล์ | Browse file | File selection |
| ที่จัดเก็บ | Save location | Output directory |
| ยกเลิก | Cancel | Abort operation |
| สถานะ | Status | Current state |
| เสร็จสิ้น | Completed / Done | Finished state |
| ผิดพลาด | Error | Failure state |
| เตือน | Warning | Caution message |

## Important Notes

1. **Output filename** always ends with `_compressed_9mb.mp4` (English, not Thai)
2. **Encoding**: all Python source files use UTF-8, supporting Thai characters directly
3. **Format strings**: Thai strings with placeholders use Python f-strings or `.format()` — keep the Thai text intact when modifying values
4. **Future i18n**: if multi-language support is needed, consider refactoring to a dictionary mapping or `gettext` library

---

Related: [[docs/features/entry-modes]] | [[docs/architecture/structure]] | [[docs/project/overview]]
