# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.1.0] - 2026-06-06

### Added
- Introduce structure for different dataset-specific tools
- `proxy` and `verify` options on the loaders for downloading behind a proxy / custom TLS
- `Matrix.to_pandas()` to convert a matrix to a labelled DataFrame
- OECD ICIO 2025 edition (`2025-regular`, `2025-extended`) and Eurostat Figaro 2025 edition (`2025`, years 2010-2023)
### Changed
- Renamed the package from `iopy` to `iotables` and adopted a `src/` layout with `pyproject.toml`
- Downloads now use `curl_cffi` (browser TLS impersonation) so Cloudflare-protected OECD files work
- Re-pointed OECD/Figaro download URLs to current hosts (OECD `webfs`, Figaro CIRCABC)
- Cached downloads now live in a user cache dir (`~/.cache/iotables`, override with `IOTABLES_DATA`)
- User-facing argument validation now raises `ValueError` instead of `assert` (so it survives `python -O`)
### Fixed
- OECD `2025-regular` file-id regex and in-zip CSV filenames; cross-edition cache-id collisions
- `remove_downloaded_files(database=...)` deleted the wrong database's files
- `ExioBase` download-failure handler raised `AttributeError` instead of the intended warning
- Loader `db_name` derivation used `str.rstrip('.py')` (a character set, not a suffix)
- Dropped `lru_cache` on `_load_data`, which pinned every loader instance (and its data) in memory
- Downloads are now atomic (written to a `.part` file and moved into place on completion), so an interrupted download no longer leaves a truncated file in the cache
- `download_file` now verifies the downloaded size against `Content-Length` (when advertised and unencoded) and raises on a truncated body
### Other
- Added a `py.typed` marker, `[project.urls]`, Python-version classifiers, and a GitHub Actions CI (offline tests across Python 3.9-3.13 + build/twine check)
- Network tests are marked `network` and moved into fixtures, so the suite collects and the offline tests run without a connection (`pytest -m "not network"`)
___


## [0.0.1] - 2022-11-22

### Added
- Born
