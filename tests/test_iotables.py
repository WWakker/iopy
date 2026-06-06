"""Offline tests for top-level helpers and the shared downloader."""
import pytest
import iotables
from iotables import utils


class TestIotables:

    def test1(self):
        iotables.remove_downloaded_files(database='figaro')

    def test_folder_size(self):
        assert isinstance(iotables.get_size_data_folder(), str)


class TestRemoveDownloadedFiles:
    """Offline tests for remove_downloaded_files (no network)."""

    def _setup_log(self, tmp_path, monkeypatch):
        oecd_file = tmp_path / 'oecd.zip'
        figaro_file = tmp_path / 'figaro.csv'
        oecd_file.write_text('x')
        figaro_file.write_text('y')
        log = tmp_path / '_files_log.txt'
        # Order matters: oecd is written first so the last line is figaro. The
        # earlier wrong-database bug used the leftover loop variable (last line),
        # which would have made remove(database='oecd') target figaro instead.
        log.write_text(f'oecd;{oecd_file}\nfigaro;{figaro_file}\n')
        monkeypatch.setattr(utils, 'FILES_LOG', str(log))
        return oecd_file, figaro_file, log

    def test_remove_single_database_keeps_others(self, tmp_path, monkeypatch):
        oecd_file, figaro_file, log = self._setup_log(tmp_path, monkeypatch)

        utils.remove_downloaded_files(database='oecd', verbose=False)

        assert not oecd_file.exists()       # requested database removed
        assert figaro_file.exists()         # other database untouched
        assert log.exists()                 # log rewritten, not deleted
        assert log.read_text().strip() == f'figaro;{figaro_file}'

    def test_remove_all(self, tmp_path, monkeypatch):
        oecd_file, figaro_file, log = self._setup_log(tmp_path, monkeypatch)

        utils.remove_downloaded_files(database='all', verbose=False)

        assert not oecd_file.exists()
        assert not figaro_file.exists()
        assert not log.exists()

    def test_remove_unknown_database_is_noop(self, tmp_path, monkeypatch):
        oecd_file, figaro_file, log = self._setup_log(tmp_path, monkeypatch)

        utils.remove_downloaded_files(database='nope', verbose=False)

        assert oecd_file.exists()
        assert figaro_file.exists()
        assert log.exists()

    def test_no_log_is_noop(self, tmp_path, monkeypatch):
        monkeypatch.setattr(utils, 'FILES_LOG', str(tmp_path / 'missing.txt'))
        utils.remove_downloaded_files(database='all', verbose=False)  # must not raise


class _FakeResponse:
    def __init__(self, chunks, headers, ok=True, status_code=200):
        self._chunks = chunks
        self.headers = headers
        self.ok = ok
        self.status_code = status_code
        self.reason = 'OK'

    def iter_content(self):
        return iter(self._chunks)


class TestDownloadFile:
    """Offline tests for download_file's atomic + integrity behaviour (no network)."""

    def _patch(self, monkeypatch, response):
        import curl_cffi
        monkeypatch.setattr(curl_cffi.requests, 'get', lambda *a, **k: response)

    def test_truncated_body_raises_and_leaves_no_files(self, tmp_path, monkeypatch):
        # Server advertises 100 bytes but only streams 50: a silent truncation.
        resp = _FakeResponse([b'x' * 50], {'Content-Length': '100'})
        self._patch(monkeypatch, resp)
        dest = tmp_path / 'data.zip'

        with pytest.raises(ConnectionError):
            utils.download_file('http://example/data.zip', str(dest))

        assert not dest.exists()
        assert not (tmp_path / 'data.zip.part').exists()

    def test_complete_body_succeeds(self, tmp_path, monkeypatch):
        resp = _FakeResponse([b'ab', b'cd'], {'Content-Length': '4'})
        self._patch(monkeypatch, resp)
        dest = tmp_path / 'data.zip'

        utils.download_file('http://example/data.zip', str(dest))

        assert dest.read_bytes() == b'abcd'
        assert not (tmp_path / 'data.zip.part').exists()

    def test_length_check_skipped_for_encoded_body(self, tmp_path, monkeypatch):
        # gzip/chunked (e.g. CIRCABC): advertised length differs from decoded bytes,
        # so the check must be skipped rather than false-positive.
        resp = _FakeResponse([b'x' * 50], {'Content-Length': '100', 'Content-Encoding': 'gzip'})
        self._patch(monkeypatch, resp)
        dest = tmp_path / 'data.csv'

        utils.download_file('http://example/data.csv', str(dest))

        assert dest.read_bytes() == b'x' * 50

    def test_no_content_length_succeeds(self, tmp_path, monkeypatch):
        resp = _FakeResponse([b'hello'], {})
        self._patch(monkeypatch, resp)
        dest = tmp_path / 'data.csv'

        utils.download_file('http://example/data.csv', str(dest))

        assert dest.read_bytes() == b'hello'

    def test_http_error_raises(self, tmp_path, monkeypatch):
        resp = _FakeResponse([], {}, ok=False, status_code=504)
        resp.reason = 'Gateway Timeout'
        self._patch(monkeypatch, resp)
        dest = tmp_path / 'data.zip'

        with pytest.raises(ConnectionError):
            utils.download_file('http://example/data.zip', str(dest))

        assert not dest.exists()
