"""  Created on 22/11/2022::
------------- test_iopy -------------
**Authors**: W. Wakker

"""
import iopy


class TestIopy:

    def test1(self):
        iopy.remove_downloaded_files(database='figaro')

    def test_folder_size(self):
        assert isinstance(iopy.get_size_data_folder(), str)
