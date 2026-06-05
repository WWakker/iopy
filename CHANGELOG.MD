# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased] - yyyy-mm-dd

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
### Fixed
- OECD `2025-regular` file-id regex and in-zip CSV filenames; cross-edition cache-id collisions
___


## [0.0.1] - 2022-11-22

### Added
- Born
