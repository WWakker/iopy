"""Network tests for the ExioBase loader (download real data; run with the 'network' marker)."""
import pytest
from iotables import ExioBase


@pytest.mark.network
class TestExioBase:

    def test_load(self):
        ex = ExioBase(version='3.81', year=2022, kind='industry-by-industry')
        assert set(ex.sectors).issubset(ex.sector_name_mapping)
        ex = ExioBase(version='3.81', year=2022, kind='product-by-product')
        assert set(ex.sectors).issubset(ex.sector_name_mapping)
