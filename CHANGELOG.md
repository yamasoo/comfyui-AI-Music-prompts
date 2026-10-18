# Changelog

All notable changes to this project are documented in this file.

## [1.2.0] - 2026-10-18

### Added
- Cover image support for every output format: the `image` input is saved as a sidecar `.png`, embedded as front-cover art in MP3 (ID3 APIC) and FLAC (PICTURE) files, and still used as the video frame for MP4.
- New optional `embed_cover` toggle on the saver node.
- `requirements.txt` (`av`, optional `mutagen`) so ComfyUI Manager installs dependencies automatically.
- `example_workflows/` folder; ComfyUI lists these workflows in its template browser.

### Changed
- Genre and mood data now live only in `prompt_data.py`; the unused duplicate tables inside the generator were removed.
- Node display names are defined once in each module and merged by `__init__.py`.
- Wildcard debug logging is off by default (`DEBUG_WILDCARD = False`); the "no wildcard JSON found" warning prints once per language/mode/genre instead of on every run.
- MP4 export converts the cover to yuv420p once instead of once per frame.
- README rewritten to match the current inputs, install steps and node names.

### Fixed
- Output numbering is shared across mp3 / flac / mp4 and sidecar files, so switching formats no longer overwrites an earlier track's `.txt` (or `.png`).
- Cover images connected while saving as MP3 or FLAC were silently discarded.

## [1.1.0] - 2026-09-19

### Added
- Added selectable audio output formats: MP3, FLAC, and MP4.
- Added lossless same-format copying when the upstream source is already in the requested output format.
- Added MP4 export support with a static cover image and synchronized audio stream for YouTube-friendly delivery.
- Added extended genre and mood prompt data to enrich prompt generation quality.
- Added lyric-related file support and metadata output for generated assets.
- Added more explicit metadata writing alongside generated audio output.

### Changed
- Refactored the generator logic to remove duplicated lyrics handling and improve maintainability.
- Improved genre and instrument handling to better support fallback and validation scenarios.
- Tightened output path and filename sanitization to prevent unsafe directory usage and malformed filenames.
- Improved waveform normalization for common ComfyUI audio tensor layouts.
- Clarified project documentation in the README to match the actual supported workflow and fallback behavior.

### Fixed
- Fixed MP3/FLAC mux timestamp issues by setting explicit time bases and packet presentation timestamps during encoding.
- Fixed waveform and source audio detection for common upstream audio formats.
- Fixed wildcard JSON discovery and validation so prompt data files are found reliably even when folder names or file names vary slightly.
- Fixed partial-file cleanup behavior so failed encodes do not leave behind misleading output artifacts.
- Fixed handling of nested subfolders while preventing path traversal outside ComfyUI's output directory.

### Notes
- When exporting MP4, a cover image is embedded into the video stream rather than saved separately as a sidecar PNG.
- Output file names are sanitized and auto-indexed to avoid collisions across repeated generations.
- The plugin now preserves a more robust generation workflow for both prompt generation and audio export.

## [Initial Release] - 2026-09-18

### Added
- Initial project setup for Ace-Step music prompt generation and output handling.
- Support for saving generated music output with metadata alongside prompt and lyric text.
- ComfyUI node integration for export and result handling.

