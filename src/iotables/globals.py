"""  Created on 22/11/2022::
------------- globals -------------
**Authors**: W. Wakker

"""
import os

# Downloaded source files are cached in a user-level cache directory rather than inside
# the installed package. Override with the IOTABLES_DATA environment variable; otherwise
# fall back to XDG_CACHE_HOME (or ~/.cache) per platform convention.
_cache_root = os.environ.get('XDG_CACHE_HOME') or os.path.join(os.path.expanduser('~'), '.cache')
DATA_FOLDER = os.environ.get('IOTABLES_DATA', os.path.join(_cache_root, 'iotables'))
IS_WINDOWS = os.name == 'nt'
FILES_LOG = os.path.join(DATA_FOLDER, '_files_log.txt')
