"""  Created on 03/10/2022::
------------- test -------------
**Authors**: W. Wakker

"""
import pytest
from iopy import OECD
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

oecd = OECD(version='2021', year=2018)

custom_shock_vector = np.random.uniform(size=oecd.rs, low=-10, high=10).reshape(-1, 1)

EA = ['AT', 'BE', 'CY', 'DE', 'EE', 'ES', 'FI', 'FR', 'GR', 'HR', 'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PT', 'SI', 'SK']


class TestOECD:

    def test_download(self):
        o = OECD(version='2021', year=2018, refresh=True)

    def test_load(self):
        o = OECD(version='2021', year=2018)
        assert set(o.sectors).issubset(o.sector_name_mapping)
        o = OECD(version='2022-extended', year=2018)
        assert set(o.sectors).issubset(o.sector_name_mapping)
        o = OECD(version='2022-small', year=2018)
        assert set(o.sectors).issubset(o.sector_name_mapping)

    def test_matrices(self):
        for attr in ['Z', 'A', 'B', 'L', 'G', 'V', 'FD', 'X']:
            assert hasattr(oecd, attr)
            for attr_attr in ['info', 'rows', 'columns', 'I']:
                assert attr_attr in dir(getattr(oecd, attr))

    def test_leontief(self):
        fd = (np.eye(oecd.rs) - oecd.A) @ oecd.X
        assert np.isclose(oecd.FD, fd, atol=.001).all()

        x = (np.eye(oecd.rs) - oecd.A).I @ oecd.FD
        assert np.isclose(oecd.X, x, atol=.001).all()

    def test_ghosh(self):
        x = oecd.G.T @ oecd.V.T
        assert np.isclose(oecd.X, x, atol=.001).all()

    def test_shock(self):
        assert np.array_equal(oecd._shock(model='ghosh', custom_shock_vector=custom_shock_vector),
                              (oecd.G.T @ (oecd.V.T * (custom_shock_vector / 100))) + oecd.X)

        assert np.array_equal(oecd._shock(model='leontief', custom_shock_vector=custom_shock_vector),
                              ((np.eye(oecd.rs) - oecd.A).I @ (
                                      oecd.FD * (custom_shock_vector / 100))) + oecd.X)

        with pytest.raises(AssertionError):
            oecd._shock(model='leontief')

        shock_vector = np.array([-.1 if r in EA and s == '35' else 0 for r, s in oecd.X.rows]).reshape(-1, 1)
        assert np.array_equal(oecd._shock(model='ghosh', shock=-10, regions=EA, sectors=['35']),
                              (oecd.G.T @ (oecd.V.T * (shock_vector.astype('float64')))) + oecd.X)

        assert np.array_equal(oecd._shock(model='leontief', shock=-10, regions=EA, sectors=['35']),
                              ((np.eye(oecd.rs) - oecd.A).I @ (
                                      oecd.FD * shock_vector.astype('float64'))) + oecd.X)

        with pytest.raises(ValueError):
            oecd._shock(model='something', shock=-10, regions=EA, sectors=['35'])

        with pytest.raises(ValueError):
            oecd._shock(model='leontief', shock=-10, regions=EA, sectors=['something'])

        with pytest.raises(ValueError):
            oecd._shock(model='leontief', shock=-10, regions=EA + ['something'], sectors=['35'])

    def test_leontief_shock(self):
        assert np.array_equal(
            oecd.leontief_demand_shock(shock=-10, regions=EA, sectors=['35']).x_new.values.reshape(-1, 1),
            oecd._shock(model='leontief', shock=-10, regions=EA, sectors=['35']))

    def test_ghosh_shock(self):
        assert np.array_equal(
            oecd.ghosh_supply_shock(shock=-10, regions=EA, sectors=['35']).x_new.values.reshape(-1, 1),
            oecd._shock(model='ghosh', shock=-10, regions=EA, sectors=['35']))

    def test_plot(self):
        fig, ax = oecd.ghosh_supply_shock(shock=-10, regions=EA, sectors=['35'], plot=True, show=False)
        assert isinstance(fig, matplotlib.figure.Figure)
        assert isinstance(ax, plt.Axes)

        fig, ax1 = oecd.ghosh_supply_shock(shock=-10, regions=EA, sectors=['35'], plot=True, show=True,
                                           plot_by='sector')
        fig, ax2 = oecd.ghosh_supply_shock(shock=10, regions=EA, sectors=['35'], plot=True, show=True,
                                           plot_by='sector')
        assert [x.get_text() for x in ax1.get_yticklabels()[::-1]] == [x.get_text() for x in ax2.get_yticklabels()]

        with pytest.raises(ValueError):
            oecd.ghosh_supply_shock(shock=-10, regions=EA, sectors=['35'],
                                    plot=True, show=True, plot_by='region', plot_regions=EA + ['something'])

    def test_get_imports_exports(self):

        assert np.isclose(oecd.get_imports_exports(import_regions=['CN1', 'CN2'],
                                                   export_regions='AU',
                                                   import_sectors=None,
                                                   export_sectors=None,
                                                   use_type='intermediate'), 85486.566)

        assert np.isclose(oecd.get_imports_exports(import_regions='CN',
                                                   export_regions='AU',
                                                   import_sectors=None,
                                                   export_sectors=None,
                                                   use_type='final'), 27117.093)

        assert np.isclose(oecd.get_imports_exports(import_regions=['CN', 'CN1', 'CN2'],
                                                   export_regions='AU',
                                                   import_sectors=None,
                                                   export_sectors=None,
                                                   use_type='both'), 27117.093 + 85486.566)

        oecd.get_imports_exports(import_regions=['CN', 'CN1', 'CN2'],
                                 export_regions='AU',
                                 import_sectors=['01T02'],
                                 export_sectors=None,
                                 use_type='both')

        assert oecd.get_imports_exports(import_regions=['AU'],
                                        export_regions=['CN'],
                                        use_type='both') == 0

        oecd.get_imports_exports(import_regions=['CN', 'CN1', 'CN2'],
                                 export_regions=['CN'],
                                 use_type='both')

        with pytest.raises(ValueError):
            oecd.get_imports_exports(import_regions=['CN', 'CN1', 'CN2'],
                                     export_regions=['EU'],
                                     use_type='both')

        oecd.get_imports_exports(import_regions=['CN', 'CN1', 'CN2'],
                                 export_regions=['AU'],
                                 export_sectors='01T02',
                                 import_sectors='03',
                                 use_type='both')
