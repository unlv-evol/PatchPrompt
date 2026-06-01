# Metadata Directory

This directory stores supporting provenance and metadata artifacts associated with
the replication package.

At present, this folder is intentionally minimal and may only contain this README.
Canonical provenance and integrity artifacts are maintained under:

- `Dataset_Construction/provenance/data_manifest.csv`
- `Dataset_Construction/provenance/checksums.sha256`
- `Dataset_Construction/provenance/lineage.md`

The raw inputs used by preprocessing are stored in sibling directories:

- `Dataset_Construction/raw_data/github/`
- `Dataset_Construction/raw_data/chatgpt/`
