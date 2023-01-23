import os
from iopy.core.globals import DATA_FOLDER as __DATA_FOLDER
from iopy.core.globals import IS_WINDOWS as __IS_WINDOWS
from iopy.core.globals import FILES_LOG as __FILES_LOG
from iopy.core.oecd import OECD
from iopy.core.figaro import Figaro
from iopy.core.exiobase import ExioBase
from iopy.core.utils import remove_downloaded_files


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


if not os.path.exists(__DATA_FOLDER):
    os.mkdir(__DATA_FOLDER)

del os
