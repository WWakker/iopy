"""  Created on 17/11/2022::
------------- test_exiobase -------------
**Authors**: W. Wakker

"""
from iopy import ExioBase
t


class TestExioBase:

    def test_load(self):
        ex = ExioBase(version='3.81', year=2022, kind='industry-by-industry')
        assert set(ex.sectors).issubset(ex.sector_name_mapping)
        ex = ExioBase(version='3.81', year=2022, kind='product-by-product')
        assert set(ex.sectors).issubset(ex.sector_name_mapping)
