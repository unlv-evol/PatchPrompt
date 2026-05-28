# Metadata Directory

This directory stores supporting provenance and metadata artifacts associated with
the replication package.

At present, this folder is intentionally minimal and may only contain this README.
Canonical provenance and integrity artifacts are maintained under:

- `dataset/provenance/data_manifest.csv`
- `dataset/provenance/checksums.sha256`
- `dataset/provenance/lineage.md`

The raw inputs used by preprocessing are stored in sibling directories:

- `dataset/raw/github/`
- `dataset/raw/chatgpt/`
