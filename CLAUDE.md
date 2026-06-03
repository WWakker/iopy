# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`iopy` is a Python package for loading inter-country input-output (IO) data from three
public databases (OECD ICIO, Eurostat Figaro, EXIOBASE) and running economic analyses on
them — primarily Leontief demand shocks and Ghosh supply shocks. See [README.md](README.md)
for the economic theory (Leontief/Ghosh derivations) and the full public API table.

## Commands

```bash
# Install for development (editable)
pip install -e .
pip install -r iopy/dev-requirements.txt   # runtime deps + pytest, pytest-cov

# Run the full test suite
pytest iopy/tests

# Run a single test file / test
pytest iopy/tests/test_oecd.py
pytest iopy/tests/test_oecd.py::TestOECD::test_leontief

# Coverage (config in iopy/tests/.coveragerc)
pytest --cov=iopy iopy/tests
```

Note: the tests **download real data over the network** (tens to hundreds of MB) and
instantiate the loader classes, so they are slow and require internet. Downloaded files are
cached under `iopy/.temp_data/`, so reruns are faster. `test_download` forces a re-download
with `refresh=True`.

## Architecture

The core abstraction is a **two-layer design**: a shared analysis engine and per-database loaders.

### `IO` base class — [iopy/core/base_io.py](iopy/core/base_io.py)
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
[oecd.py](iopy/core/oecd.py), [figaro.py](iopy/core/figaro.py),
[exiobase.py](iopy/core/exiobase.py). Each subclasses `IO` and follows the **same lifecycle**
inside `__init__`:
1. Validate `version`/`year`/`kind` against `config`.
2. Resolve the download URL from `config`, extract a `_file_id` via the version's `regex_id`,
   download to `DATA_FOLDER` if not already cached (or `refresh=True`).
3. Load the raw file into `self.df`, slice it into the contract matrices (`Z`, `FD`, `X`,
   `V`, `FD_REGION`, plus database-specific extras in the `ADD` dict).
4. Call `super().__init__()` **last** to build `A`/`L`/`B`/`G`.

When adding a new data version or year, the change is almost always **data-only**: add the
download links and `num_regions`/`num_sectors`/`regex_id` to
[iopy/core/config.py](iopy/core/config.py). Each loader has a module-level `process_df`
helper that converts the raw dataframe index/columns into `(region, sector)` tuples — the
three differ because each source formats its labels differently (OECD maps ISO alpha-3 →
alpha-2 via `ALPHA3_TO_ALPHA2`; EXIOBASE uses MultiIndex columns).

### `Matrix` — [iopy/core/matrix.py](iopy/core/matrix.py)
A thin `numpy.ndarray` subclass carrying `info` (label), `rows`, and `columns` metadata
(lists of `(region, sector)` tuples), plus `.I` (inverse) and `.T` (transpose that also swaps
row/column labels). All IO matrices are `Matrix` instances; row/column selection in
`get_imports_exports` relies on these label lists.

### Supporting modules
- [config.py](iopy/core/config.py) — nested dict of `{database: {version: {links, regex_id,
  num_regions, num_sectors}}}`. The single source of truth for what data exists.
- [mappings.py](iopy/core/mappings.py) — sector-code → human-name dicts and demand-item lists
  per database; also the OECD 2022→2021 sector-code remapping.
- [globals.py](iopy/core/globals.py) — `DATA_FOLDER` (`iopy/.temp_data`), `FILES_LOG`,
  `IS_WINDOWS`.
- [utils.py](iopy/core/utils.py) — `assert_is_subset` (the standard validation used
  throughout), `remove_downloaded_files`, and the `ALPHA3_TO_ALPHA2` country-code map.

### Download cache and cleanup
Downloaded archives live in `DATA_FOLDER` and every download appends a `db_name;path` line to
`FILES_LOG` (`_files_log.txt`). `remove_downloaded_files(database=...)` reads that log to
delete files for one database or `'all'`. This is exposed as `iopy.remove_downloaded_files`
and as a `remove_downloaded_files` static method on each loader.

## Conventions

- The public surface is re-exported from [iopy/\_\_init\_\_.py](iopy/__init__.py): `OECD`,
  `Figaro`, `ExioBase`, `remove_downloaded_files`, `get_size_data_folder`. Keep new
  user-facing entry points exported there.
- Validation is done with `assert_is_subset` (raises `ValueError` listing what's missing) and
  plain `assert` for argument-shape checks — match this style rather than introducing custom
  exception types.
- Version strings are dict keys (e.g. `'2021'`, `'2022-extended'`, `'2025-regular'`), not
  numbers; `kind` is `'industry-by-industry'` or `'product-by-product'` (OECD has no `kind`).
