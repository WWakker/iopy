"""  Created on 22/11/2022::
------------- test_iotables -------------
**Authors**: W. Wakker

"""
import iotables


class TestIotables:

    def test1(self):
        iotables.remove_downloaded_files(database='figaro')

    def test_folder_size(self):
        assert isinstance(iotables.get_size_data_folder(), str)
