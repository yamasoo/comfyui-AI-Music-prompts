# Changelog

All notable changes to this project are documented in this file.

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

