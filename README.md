Export Bundle
=============

This folder contains an export of metadata and OCR results from `archive_tracking.db`.

Contents
- `manifest.csv` — One row per document linking `identifier` → `pdf_file_id` → `ocr_id`, with relative paths to exported JSON files.
- `documents.jsonl` — Combined metadata + PDF record info + OCR metadata per document.
- `metadata/<subcollection>/{identifier}.json` — IA metadata JSON per `identifier` (or synthesized when IA JSON not present) organized by subcollection.
- `ocr/<subcollection>/{identifier}.json` — Raw OCR pages JSON per `identifier`, exactly as stored in the database, organized by subcollection.

Notes
- No PDFs are included.
- OCR files are provided for records with completed OCR. For items without OCR, the bundle still includes metadata and a JSONL entry with `ocr.status = "missing"` and no `ocr` file.
- Relationships are preserved via `items.identifier`, `pdf_files.id`, and `ocr_processing.id`.
- Files are grouped under their `pdf_files.subcollection`.

Provenance
- Exported using `tools/export_sqlite_bundle.py` on this repository.
