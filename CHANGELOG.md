# Changelog

All notable changes to `pinarkive-sdk-py` are documented here.

## [3.1.1] - 2026-04-14

### Fixed

- **`upload_directory_dag` multipart format:** The API expects multer field **`files`** (repeated), with each part’s **filename** set to the relative path inside the DAG (e.g. `1.png`, `assets/logo.svg`). The SDK previously sent `files[i][path]` / `files[i][content]`, which the backend does not parse into `req.files`.

### Release / publish (GitHub Actions → PyPI)

This repo publishes on **GitHub Release published** (see `.github/workflows/publish.yml`).

Suggested steps:

1. Bump `pyproject.toml` version.
2. Commit on `main`.
3. Create a tag `v3.1.1` (or your chosen version).
4. Create a GitHub Release for that tag (publishing the release triggers the workflow).

