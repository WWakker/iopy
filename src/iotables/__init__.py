import os as _os
from importlib.metadata import version as _version, PackageNotFoundError as _PackageNotFoundError
from iotables.globals import DATA_FOLDER as __DATA_FOLDER
from iotables.globals import IS_WINDOWS as __IS_WINDOWS
from iotables.globals import FILES_LOG as __FILES_LOG
from iotables.oecd import OECD
from iotables.figaro import Figaro
from iotables.exiobase import ExioBase
from iotables.utils import remove_downloaded_files

try:
    __version__ = _version("iotables")
except _PackageNotFoundError:  # package not installed (e.g. running from source tree)
    __version__ = "0.0.0"


def get_size_data_folder():
    """Get size of the folder where downloaded files are stored

    Returns:
        str: Size of folder

    """
    from pathlib import Path

    def get_size(folder):
        def human(size):
            UNITS = ["B", "KB", "MB", "GB", "TB"]
            HUMANFMT = "{size} {unit}"
            HUMANRADIX = 1024.
            for u in UNITS[:-1]:
                if size < HUMANRADIX:
                    return HUMANFMT.format(size=round(size, 2), unit=u)
                size /= HUMANRADIX
            return HUMANFMT.format(size=round(size, 2), unit=UNITS[-1])

        root_directory = Path(folder)
        tot_size = sum(f.stat().st_size for f in root_directory.glob('**/*') if f.is_file())
        return human(tot_size)
    return get_size(__DATA_FOLDER)


_os.makedirs(__DATA_FOLDER, exist_ok=True)
