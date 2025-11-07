Export Bundle
=============

This folder contains an export of metadata and OCR results from `archive_tracking.db`.

Contents
- `manifest.csv` — One row per document linking `identifier` → `pdf_file_id` → `ocr_id`, with relative paths to exported JSON files.
- `documents.jsonl` — Combined metadata + PDF record info + OCR metadata per document.
- `metadata/` — IA metadata JSON per `identifier` (or synthesized when IA JSON not present).
- `ocr/` — Raw OCR pages JSON per `identifier`, exactly as stored in the database.

Notes
- No PDFs are included.
- All OCR records have `status = completed` and non-null `ocr_data`.
- Relationships are preserved via `items.identifier`, `pdf_files.id`, and `ocr_processing.id`.

Provenance
- Exported using `tools/export_sqlite_bundle.py` on this repository.

