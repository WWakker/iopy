# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`iotables` is a Python package for loading inter-country input-output (IO) data from three
public databases (OECD ICIO, Eurostat Figaro, EXIOBASE) and running economic analyses on
them — primarily Leontief demand shocks and Ghosh supply shocks. See [README.md](README.md)
for the economic theory (Leontief/Ghosh derivations) and the full public API table.

The package uses a `src/` layout (`src/iotables/`) with packaging configured in
[pyproject.toml](pyproject.toml); tests live in the top-level [tests/](tests/) directory.

## Commands

```bash
# Install for development (editable, with test deps)
pip install -e ".[dev]"

# Run the full test suite
pytest

# Run a single test file / test
pytest tests/test_oecd.py
pytest tests/test_oecd.py::TestOECD::test_leontief

# Coverage (config in pyproject.toml [tool.coverage])
pytest --cov=iotables
```

Note: the tests **download real data over the network** (tens to hundreds of MB) and
instantiate the loader classes, so they are slow and require internet. Downloaded files are
cached under a user cache dir (`~/.cache/iotables`, override with the `IOTABLES_DATA`
environment variable), so reruns are faster. `test_download` forces a re-download with
`refresh=True`.

## Architecture

The core abstraction is a **two-layer design**: a shared analysis engine and per-database loaders.

### `IO` base class — [src/iotables/base_io.py](src/iotables/base_io.py)
The engine. Its `__init__` asserts that the subclass has already set a fixed contract of
attributes (`Z`, `X`, `V`, `FD`, `FD_REGION`, `ADD`, `rs`, `regions`, `sectors`,
`sector_name_mapping`, `unit`, `demand_items`), then derives the coefficient and inverse
matrices from them:
- `A` = technical coefficients (`Z / X`), `L` = Leontief inverse `(I − A)⁻¹`
- `B` = allocation coefficients, `G` = Ghosh inverse `(I − B)⁻¹`

It provides the public methods `leontief_demand_shock`, `ghosh_supply_shock`, and
`get_imports_exports`, plus the private `_shock` / `_shock_to_df` / `_plot_shock` helpers.
Zeros in `X` are replaced with 1 before division so the matrices stay invertible.

### Loader classes — `OECD`, `Figaro`, `ExioBase`
[oecd.py](src/iotables/oecd.py), [figaro.py](src/iotables/figaro.py),
[exiobase.py](src/iotables/exiobase.py). Each subclasses `IO` and follows the **same lifecycle**
inside `__init__`:
1. Validate `version`/`year`/`kind` against `config`.
2. Resolve the download URL from `config`, extract a `_file_id` via the version's `regex_id`,
   download to `DATA_FOLDER` if not already cached (or `refresh=True`).
3. Load the raw file into `self.df`, slice it into the contract matrices (`Z`, `FD`, `X`,
   `V`, `FD_REGION`, plus database-specific extras in the `ADD` dict).
4. Call `super().__init__()` **last** to build `A`/`L`/`B`/`G`.

When adding a new data version or year, the change is almost always **data-only**: add the
download links and `num_regions`/`num_sectors`/`regex_id` to
[src/iotables/config.py](src/iotables/config.py). Each loader has a module-level `process_df`
helper that converts the raw dataframe index/columns into `(region, sector)` tuples — the
three differ because each source formats its labels differently (OECD maps ISO alpha-3 →
alpha-2 via `ALPHA3_TO_ALPHA2`; EXIOBASE uses MultiIndex columns).

### `Matrix` — [src/iotables/matrix.py](src/iotables/matrix.py)
A thin `numpy.ndarray` subclass carrying `info` (label), `rows`, and `columns` metadata
(lists of `(region, sector)` tuples), plus `.I` (inverse) and `.T` (transpose that also swaps
row/column labels). All IO matrices are `Matrix` instances; row/column selection in
`get_imports_exports` relies on these label lists.

### Supporting modules
- [config.py](src/iotables/config.py) — nested dict of `{database: {version: {links, regex_id,
  num_regions, num_sectors}}}`. The single source of truth for what data exists.
- [mappings.py](src/iotables/mappings.py) — sector-code → human-name dicts and demand-item lists
  per database; also the OECD 2022→2021 sector-code remapping.
- [globals.py](src/iotables/globals.py) — `DATA_FOLDER` (`~/.cache/iotables`, `IOTABLES_DATA` override), `FILES_LOG`,
  `IS_WINDOWS`.
- [utils.py](src/iotables/utils.py) — `assert_is_subset` (the standard validation used
  throughout), `remove_downloaded_files`, the `ALPHA3_TO_ALPHA2` country-code map, and
  `download_file` (the single shared downloader used by all three loaders).

### Downloading
All three loaders download via `utils.download_file`, which uses **`curl_cffi`** with browser
TLS impersonation (`impersonate='chrome'`). This is required because the OECD file server
(`webfs-sti.oecd.org`) sits behind Cloudflare and rejects plain `requests`/`urllib` with HTTP
403; impersonation is harmless for the Eurostat (CIRCABC) and EXIOBASE (Zenodo) hosts. Each
loader's `__init__` accepts `proxy=` (URL string or `{scheme: url}` dict) and `verify=`
(TLS verification toggle / CA-bundle path), threaded through to `download_file`.

### Download cache and cleanup
Downloaded archives live in `DATA_FOLDER` and every download appends a `db_name;path` line to
`FILES_LOG` (`_files_log.txt`). `remove_downloaded_files(database=...)` reads that log to
delete files for one database or `'all'`. This is exposed as `iotables.remove_downloaded_files`
and as a `remove_downloaded_files` static method on each loader.

## Conventions

- The public surface is re-exported from [src/iotables/\_\_init\_\_.py](src/iotables/__init__.py): `OECD`,
  `Figaro`, `ExioBase`, `remove_downloaded_files`, `get_size_data_folder`. Keep new
  user-facing entry points exported there.
- Validation is done with `assert_is_subset` (raises `ValueError` listing what's missing) and
  plain `assert` for argument-shape checks — match this style rather than introducing custom
  exception types.
- Version strings are dict keys (e.g. `'2021'`, `'2022-extended'`, `'2025-regular'`), not
  numbers; `kind` is `'industry-by-industry'` or `'product-by-product'` (OECD has no `kind`).
