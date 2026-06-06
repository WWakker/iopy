"""  Created on 22/11/2022::
------------- test_iotables -------------
**Authors**: W. Wakker

"""
import os
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
