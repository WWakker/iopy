"""  Created on 18/10/2022::
------------- io -------------
**Authors**: W. Wakker

"""
from warnings import warn
from iopy.core.matrix import Matrix
from iopy.core.utils import assert_is_subset
import matplotlib.pyplot as plt
from typing import Union, Iterable, Optional
import numpy as np
import pandas as pd


class IO:
    """Class for creating standard IO matrices and IO helper functions, meant as a parent
    class for classes that load IO data.
    """

    def __init__(self):
        necessary_attrs = ['Z',
                           'X',
                           'V',
                           'FD',
                           'ADD',
                           'FD_REGION',
                           'rs',
                           'sector_name_mapping',
                           'regions',
                           'sectors',
                           'unit',
                           'demand_items']
        assert_is_subset(necessary_attrs, dir(self))

        # Coefficients matrix, replace 0 with 1 to allow inversion
        x_filled = self.X.copy()
        x_filled[x_filled == 0] = 1

        # Leontief demand side
        self.A = Matrix('Technical coefficients',
                        self.Z / x_filled.flatten(),
                        self.Z.rows,
                        self.Z.columns)

        self.L = Matrix('Leontief inverse',
                        (np.eye(self.rs) - self.A).I,
                        self.Z.rows,
                        self.Z.columns)

        # Ghosh supply side
        self.B = Matrix('Allocation coefficients',
                        self.Z / x_filled,
                        self.Z.rows,
                        self.Z.columns)

        self.G = Matrix('Output inverse',
                        (np.eye(self.rs) - self.B).I,
                        self.Z.rows,
                        self.Z.columns)

    def _shock(self,
               model: str,
               shock: Union[int, float, None] = None,
               regions: Optional[Iterable] = None,
               sectors: Optional[Iterable] = None,
               custom_shock_vector: Optional[Iterable] = None):
        """Calculates new output using Leontief or Ghosh model

        Args:
            model: leontief or ghosh
            shock: Shock in percentage of original final demand or primary inputs
            regions: List of regions to be shocked
            sectors: List of sectors to be shocked
            custom_shock_vector: Vector of length regions * sectors with percentage shocks, overrides all other shock
                                 parameters if supplied

        Returns:
            Matrix: Shocked output
        """
        if custom_shock_vector is not None:
            shock_vector = np.array(custom_shock_vector).reshape(self.rs, 1)
        else:
            assert shock and regions and sectors, "Must supply parameters: 'shock', 'regions', 'sectors'"

            assert_is_subset(regions, self.regions)
            assert_is_subset(sectors, self.sectors)

            shock_vector = np.array([shock if r in regions and s in sectors
                                     else 0 for r, s in self.X.rows]).reshape(-1, 1)
        shock_vector = shock_vector.astype('float64')
        shock_vector /= 100
        if model == 'leontief':
            x_new = (self.L @ (self.FD * shock_vector)) + self.X
        elif model == 'ghosh':
            x_new = (self.G.T @ (self.V.T * shock_vector)) + self.X
        else:
            raise ValueError('model must be leontief or ghosh')

        return x_new

    def _shock_to_df(self,
                     x_new: Matrix):
        """Creates a pandas dataframe with columns: region, sector, x and x_new

        Args:
            x_new: New output

        Returns:
            pd.DataFrame
        """

        return pd.DataFrame({'region': [r for r, s in self.X.rows],
                             'sector': [s for r, s in self.X.rows],
                             'x': self.X.flatten(),
                             'x_new': x_new.flatten()})

    def _shock_and_plot(self,
                        model: str,
                        shock: Union[int, float, None] = None,
                        regions: Optional[Iterable] = None,
                        sectors: Optional[Iterable] = None,
                        custom_shock_vector: Optional[Iterable] = None,
                        plot: bool = False,
                        plot_by: str = 'region',
                        plot_regions: Optional[Iterable] = None,
                        show: bool = True,
                        ):
        """Executes a Leontief demand or Ghosh supply shock

        Args:
            model: leontief or ghosh
            shock: Shock in percentage of original final demand or primary inputs
            regions: List of regions to be shocked
            sectors: List of sectors to be shocked
            custom_shock_vector: Vector of length regions * sectors with percentage shocks, overrides all other shock
                                 parameters if supplied
            plot: Plot if true
            plot_by: region or sector; if sector, the top 20 is shown
            plot_regions: List of regions to plot the effect for
            show: Show the plot if true

        Returns:
            pd.DataFrame: df with shocked output vector if plot is False, else matplotlib fig, ax
        """
        x_new = self._shock(model=model, shock=shock, regions=regions, sectors=sectors,
                            custom_shock_vector=custom_shock_vector)

        if plot:
            if plot_regions is None:
                raise ValueError("Please specify 'plot_regions'")
            fig, ax = self._plot_shock(x_new=x_new, model=model, by=plot_by, regions=plot_regions)
            if show:
                plt.show()
            return fig, ax

        return self._shock_to_df(x_new)

    def _plot_shock(self,
                    x_new: Matrix,
                    model: str,
                    by: str,
                    regions: Iterable):
        """Plot shock from a given new output

        Args:
            x_new: New output
            model: ghosh or leontief
            by: region or sector
            regions: List of regions to plot the effect for

        Returns:
            fig, ax
        """
        assert by in {'region', 'sector'}, "plot_by must be 'region' or 'sector'"
        assert_is_subset(regions, self.regions)

        df = self._shock_to_df(x_new)
        df['diff'] = (df.x_new / df.x - 1).fillna(0)
        df['col'] = self.V.flatten() if model == 'leontief' else self.FD.flatten()
        df['newcol'] = df['col'] * (1 + df['diff'])

        df = df[df.region.isin(regions)].groupby(by)[['col', 'newcol']].sum(0)
        if by == 'sector':
            df.index = df.index.map(self.sector_name_mapping).str[:25]
        df['diff'] = (100 * (df.newcol / df.col - 1)).fillna(0)
        df.sort_values('diff', inplace=True, ascending=False)
        if by == 'sector':
            if df['diff'].mean() < 0:
                df = df.tail(20)
            else:
                df = df.head(20)

        fig, ax = plt.subplots()
        ax.barh(df.index,
                df['diff']
                )

        if df['diff'].mean() < 0:
            ax.invert_xaxis()
        else:
            ax.invert_yaxis()

        plt.xlabel(f"% change in {'GVA' if model == 'leontief' else 'final demand'}")

        plt.tight_layout()

        return fig, ax

    def leontief_demand_shock(self,
                              shock: Union[int, float, None] = None,
                              regions: Optional[Iterable] = None,
                              sectors: Optional[Iterable] = None,
                              custom_shock_vector: Optional[Iterable] = None,
                              plot: bool = False,
                              plot_by: str = 'region',
                              plot_regions: Optional[Iterable] = None,
                              show: bool = True,
                              ):
        """Executes a Leontief demand shock

        Args:
            shock: Shock in percentage of original demand
            regions: List of regions to be shocked
            sectors: List of sectors to be shocked
            custom_shock_vector: Vector of length regions * sectors with percentage shocks, overrides all other shock
                                 parameters if supplied
            plot: Plot if true
            plot_by: region or sector; if sector, the top 20 is shown
            plot_regions: List of regions to plot the effect for
            show: Show the plot if true

        Returns:
            pd.DataFrame: df with shocked output vector if plot is False, else matplotlib fig, ax
        """
        return self._shock_and_plot(model='leontief',
                                    shock=shock,
                                    regions=regions,
                                    sectors=sectors,
                                    custom_shock_vector=custom_shock_vector,
                                    plot=plot,
                                    plot_by=plot_by,
                                    plot_regions=plot_regions,
                                    show=show)

    def ghosh_supply_shock(self,
                           shock: Union[int, float, None] = None,
                           regions: Optional[Iterable] = None,
                           sectors: Optional[Iterable] = None,
                           custom_shock_vector: Optional[Iterable] = None,
                           plot: bool = False,
                           plot_by: str = 'region',
                           plot_regions: Optional[Iterable] = None,
                           show: bool = True,
                           ):
        """Executes a Ghosh supply shock

        Args:
            shock: Shock in percentage of original demand
            regions: List of regions to be shocked
            sectors: List of sectors to be shocked
            custom_shock_vector: Vector of length regions * sectors with percentage shocks, overrides all other shock
                                 parameters if supplied
            plot: Plot if true
            plot_by: region or sector; if sector, the top 20 is shown
            plot_regions: List of regions to plot the effect for
            show: Show the plot if true

        Returns:
            pd.DataFrame: df with shocked output vector if plot is False, else matplotlib fig, ax
        """
        return self._shock_and_plot(model='ghosh',
                                    shock=shock,
                                    regions=regions,
                                    sectors=sectors,
                                    custom_shock_vector=custom_shock_vector,
                                    plot=plot,
                                    plot_by=plot_by,
                                    plot_regions=plot_regions,
                                    show=show)

    def get_imports_exports(self,
                            import_regions: Iterable,
                            export_regions: Iterable,
                            import_sectors: Optional[Iterable] = None,
                            export_sectors: Optional[Iterable] = None,
                            use_type: str = 'both'):
        """Get imports and exports between regions and sectors. Use is broken down by intermediate use and final demand,
           specify 'use_type' to get either of them or both summed together.

        Args:
            import_regions: List of importing regions
            export_regions: List of exporting regions
            import_sectors: List of importing sectors, all sectors by default, only accounts for intermediate import sectors
            export_sectors: List of exporting sectors, all sectors by default
            use_type: 'intermediate', 'final', or 'both'

        Returns:
            float: Sum of trade flow from exporting region-sectors to importing region-sectors
        """
        assert use_type in {'intermediate', 'final', 'both'}, "use_type must be 'intermediate', 'final' or 'both'"

        if import_sectors is not None and use_type in {'final', 'both'}:
            warn('Note that import_sectors only apply to intermediate use, for final use only import_regions is used')

        if import_sectors is None:
            import_sectors = self.sectors
        if export_sectors is None:
            export_sectors = self.sectors

        if isinstance(import_regions, str):
            import_regions = [import_regions]
        if isinstance(export_regions, str):
            export_regions = [export_regions]
        if isinstance(import_sectors, str):
            import_sectors = [import_sectors]
        if isinstance(export_sectors, str):
            export_sectors = [export_sectors]

        for subset, superset in zip([import_regions, export_regions, import_sectors, export_sectors],
                                    [self.regions, self.regions, self.sectors, self.sectors]):
            assert_is_subset(subset, superset)

        if set(import_regions).intersection(export_regions):
            warn(f'There is overlap between import_regions and export_regions: '
                 f'{", ".join(set(import_regions).intersection(export_regions))}')

        intermediate = float(self.Z[np.ix_([r in export_regions and s in export_sectors for r, s in self.Z.rows],
                                           [r in import_regions and s in import_sectors for r, s in
                                            self.Z.columns])].sum())

        final = float(
            self.FD_REGION[np.ix_([r in export_regions and s in export_sectors for r, s in self.FD_REGION.rows],
                                  [r in import_regions for r in self.FD_REGION.columns])].sum())

        return {'intermediate': intermediate,
                'final': final,
                'both': intermediate + final}[use_type]
