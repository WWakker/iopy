"""  Created on 22/11/2022::
------------- adjust_source_in_covxml -------------
**Authors**: W. Wakker

"""
import re
import os

parent = os.path.dirname(__file__)
with open(f'{parent}/cov.xml', 'r+') as f:
    covxml = f.read()
    covxml = re.sub(r'<source>.*</source>',
                    r'<source>/builds/.../.../iopy/iopy</source>',
                    covxml)
    f.seek(0)
    f.write(covxml)
    f.truncate()
