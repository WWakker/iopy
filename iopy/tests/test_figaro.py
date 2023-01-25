"""  Created on 19/10/2022::
------------- test_figaro -------------
**Authors**: W. Wakker

"""
import pytest
from iopy import Figaro
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

f = Figaro(version='2022', year=2018, kind='industry-by-industry')

custom_shock_vector = np.random.uniform(size=f.rs, low=-10, high=10).reshape(-1, 1)

EA = ['AT', 'BE', 'CY', 'DE', 'EE', 'ES', 'FI', 'FR', 'GR', 'HR', 'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PT', 'SI', 'SK']


class TestFigaro:

    def test_download(self):
        Figaro(version='2022', year=2018, refresh=True)

    def test_load(self):
        fi = Figaro(version='2022', year=2018, kind='industry-by-industry')
        assert set(fi.sectors).issubset(fi.sector_name_mapping)
        fi = Figaro(version='2022', year=2018, kind='product-by-product')
        assert set(fi.sectors).issubset(fi.sector_name_mapping)

    def test_matrices(self):
        for attr in ['Z', 'A', 'B', 'L', 'G', 'V', 'FD', 'X']:
            assert hasattr(f, attr)
            for attr_attr in ['info', 'rows', 'columns', 'I']:
                assert attr_attr in dir(getattr(f, attr))

    def test_leontief(self):
        fd = (np.eye(f.rs) - f.A) @ f.X
        assert np.isclose(f.FD, fd, atol=.001).all()

        x = (np.eye(f.rs) - f.A).I @ f.FD
        assert np.isclose(f.X, x, atol=.001).all()

    def test_ghosh(self):
        x = f.G.T @ f.V.T
        assert np.isclose(f.X, x, atol=.001).all()

    def test_shock(self):
        assert np.array_equal(f._shock(model='ghosh', custom_shock_vector=custom_shock_vector),
                              (f.G.T @ (f.V.T * (custom_shock_vector / 100))) + f.X)

        assert np.array_equal(f._shock(model='leontief', custom_shock_vector=custom_shock_vector),
                              ((np.eye(f.rs) - f.A).I @ (
                                      f.FD * (custom_shock_vector / 100))) + f.X)

        with pytest.raises(AssertionError):
            f._shock(model='leontief')

        shock_vector = np.array([-.1 if r in EA and s == 'A01' else 0 for r, s in f.X.rows]).reshape(-1, 1)
        assert np.array_equal(f._shock(model='ghosh', shock=-10, regions=EA, sectors=['A01']),
                              (f.G.T @ (f.V.T * (shock_vector.astype('float64')))) + f.X)

        assert np.array_equal(f._shock(model='leontief', shock=-10, regions=EA, sectors=['A01']),
                              ((np.eye(f.rs) - f.A).I @ (
                                      f.FD * shock_vector.astype('float64'))) + f.X)

        with pytest.raises(ValueError):
            f._shock(model='something', shock=-10, regions=EA, sectors=['A01'])

        with pytest.raises(ValueError):
            f._shock(model='leontief', shock=-10, regions=EA, sectors=['something'])

        with pytest.raises(ValueError):
            f._shock(model='leontief', shock=-10, regions=EA + ['something'], sectors=['A01'])

    def test_leontief_shock(self):
        assert np.array_equal(
            f.leontief_demand_shock(shock=-10, regions=EA, sectors=['A01']).x_new.values.reshape(-1, 1),
            f._shock(model='leontief', shock=-10, regions=EA, sectors=['A01']))

    def test_ghosh_shock(self):
        assert np.array_equal(
            f.ghosh_supply_shock(shock=-10, regions=EA, sectors=['A01']).x_new.values.reshape(-1, 1),
            f._shock(model='ghosh', shock=-10, regions=EA, sectors=['A01']))

    def test_plot(self):
        fig, ax = f.ghosh_supply_shock(shock=-10, regions=EA, sectors=['A01'], plot_regions=EA, plot=True, show=False)
        assert isinstance(fig, matplotlib.figure.Figure)
        assert isinstance(ax, plt.Axes)

        fig, ax1 = f.ghosh_supply_shock(shock=-10, regions=EA, sectors=['A01'], plot_regions=EA, plot=True, show=True,
                                        plot_by='sector')
        fig, ax2 = f.ghosh_supply_shock(shock=10, regions=EA, sectors=['A01'], plot_regions=EA, plot=True, show=True,
                                        plot_by='sector')
        assert [x.get_text() for x in ax1.get_yticklabels()[::-1]] == [x.get_text() for x in ax2.get_yticklabels()]

        with pytest.raises(ValueError):
            f.ghosh_supply_shock(shock=-10, regions=EA, sectors=['35'],
                                 plot=True, show=True, plot_by='region', plot_regions=EA + ['something'])

        with pytest.raises(ValueError):
            f.ghosh_supply_shock(shock=-10, regions=EA, sectors=['35'],
                                 plot=True, show=True, plot_by='region')

    def test_get_imports_exports(self):

        assert np.isclose(f.get_imports_exports(import_regions=['CN'],
                                                export_regions='AU',
                                                import_sectors=None,
                                                export_sectors=None,
                                                use_type='intermediate'), 86280.8749)

        assert np.isclose(f.get_imports_exports(import_regions='CN',
                                                export_regions='AU',
                                                import_sectors=None,
                                                export_sectors=None,
                                                use_type='final'), 13770.405)

        assert np.isclose(f.get_imports_exports(import_regions=['CN'],
                                                export_regions='AU',
                                                import_sectors=None,
                                                export_sectors=None,
                                                use_type='both'), 86280.8749 + 13770.405)

        f.get_imports_exports(import_regions=['CN'],
                              export_regions='AU',
                              import_sectors=['A01'],
                              export_sectors=None,
                              use_type='both')

        f.get_imports_exports(import_regions=['CN'],
                              export_regions=['CN'],
                              use_type='both')

        with pytest.raises(ValueError):
            f.get_imports_exports(import_regions=['CN'],
                                  export_regions=['EU'],
                                  use_type='both')

        f.get_imports_exports(import_regions=['CN'],
                              export_regions=['AU'],
                              export_sectors='A01',
                              import_sectors='A01',
                              use_type='both')

    def test_remove_local_files(self):
        f.remove_downloaded_files()
