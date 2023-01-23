"""  Created on 22/11/2022::
------------- globals -------------
**Authors**: W. Wakker

"""
import os

DATA_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.temp_data')
IS_WINDOWS = os.name == 'nt'
FILES_LOG = os.path.join(DATA_FOLDER, '_files_log.txt')
