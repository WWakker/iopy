"""  Created on 14/10/2022::
------------- figaro -------------
**Authors**: W. Wakker

"""
from iopy.core.mappings import figaro_sector_name_mapping_pxp_2022, figaro_sector_name_mapping_ixi_2022, figaro_demand_items
from iopy.core.matrix import Matrix
from functools import lru_cache
import numpy as np
import pandas as pd
from tqdm import tqdm
import re
import os
from iopy.core.config import config
from warnings import warn
from iopy.core.base_io import IO
from iopy.core.globals import DATA_FOLDER, FILES_LOG
from iopy.core.utils import remove_downloaded_files

db_name = os.path.basename(__file__).rstrip('.py')


def process_df(df):
    if df.shape[0] > 1 and df.shape[1] > 1:
        return (df,
                [(r, s) for r, s in df.index.str.split('_', n=1)],
                [(r, s) for r, s in df.columns.str.split('_', n=1)])
    elif df.shape[0] == 1:
        return (df,
                df.index.to_list(),
                [(r, s) for r, s in df.columns.str.split('_', n=1)])
    else:
        return (df,
                [(r, s) for r, s in df.index.str.split('_', n=1)],
                df.columns.to_list())


class Figaro(IO):
    """Class to load and work with Figaro input-output data"""

    def __init__(self,
                 version: str,
                 year: int,
                 kind='industry-by-industry',
                 refresh: bool = False):
        """

        Args:
            version: Edition (year of publication), e.g. '2022'
            year: Year from 2010 to 2020
            kind: industry-by-industry (default) or product-by-product
            refresh: Download the data even if it exists on the hard drive
        """
        assert kind in {'industry-by-industry', 'product-by-product'}

        if version not in config['figaro'].keys():
            raise ValueError(
                f"Version selected not recognized. \n Please choose among {list(config['figaro'].keys())}")

        if year not in config['figaro'][version]['links'][kind].keys():
            raise ValueError(
                f"Year selected not present in the {version} version. \n "
                f"Please choose among {list(config['figaro'][version]['links'][kind].keys())} or consider changing version.")

        self.version = version
        self.year = year
        self.kind = kind
        self._url = config['figaro'][version]['links'][kind][year]
        self._file_id = re.search(config['figaro'][version]['regex_id'], self._url).group(0)
        self._data_file = os.path.join(DATA_FOLDER, self._file_id + '.csv')
        file_exists = os.path.exists(self._data_file)
        download = not file_exists or refresh
        with tqdm(total=3 if download else 2) as pbar:
            # Download
            if download:
                pbar.set_description('Downloading data...')
                self._download_data()
                pbar.update()

            # Load
            pbar.set_description('Loading data...')
            self.df = self._load_data()
            pbar.update()

            # Create matrices
            pbar.set_description('Creating matrices...')
            self.rs = config['figaro'][version]['num_regions'] * config['figaro'][version]['num_sectors']
            self.Z = Matrix('Intermediate use',
                            *process_df(self.df.iloc[:self.rs, :self.rs]))
            self.FD_GRAN = Matrix('Final demand granular',
                                  self.df.iloc[:self.rs, self.rs:],
                                  rows=[(r, s) for r, s in self.df.iloc[:self.rs, self.rs:].index.str.split('_', n=1)],
                                  columns=[(r, s) for r, s in
                                           self.df.iloc[:self.rs, self.rs:].columns.str.split('_', n=1)])
            self.FD = Matrix('Final demand',
                             self.FD_GRAN.sum(1).reshape(-1, 1),
                             rows=self.Z.rows,
                             columns=['FD'])
            self.X = Matrix('X',
                            self.FD + self.Z.sum(1).reshape(-1, 1),
                            rows=self.Z.rows,
                            columns=['X'])
            GVA_GRAN = Matrix('Value added granular',
                              self.df.iloc[self.rs:, :self.rs],
                              [(r, s) for r, s in self.df.iloc[self.rs:, :self.rs].index.str.split('_', n=1)],
                              [(r, s) for r, s in self.df.iloc[self.rs:, :self.rs].columns.str.split('_', n=1)])
            self.V = Matrix('GVA',
                            (self.X.flatten() - self.Z.sum(0).flatten()).reshape(1, len(self.X)),
                            rows=['GVA'],
                            columns=self.Z.columns)

            self.ADD = {'GVA_GRAN': GVA_GRAN}

            # Create region level FD
            fd_region = pd.DataFrame(self.FD_GRAN, columns=[r for r, s in self.FD_GRAN.columns]).T
            fd_region.index.name = 'region'
            fd_region = fd_region.groupby('region').sum(0).T
            self.FD_REGION = Matrix('Final demand by region',
                                    fd_region,
                                    rows=self.Z.rows,
                                    columns=fd_region.columns.to_list())

            self.regions = list(sorted(np.unique([r for r, s in self.Z.rows])))
            self.sectors = list(sorted(np.unique([s for r, s in self.Z.rows])))
            self.unit = 'Million EUR'
            self.sector_name_mapping = figaro_sector_name_mapping_ixi_2022 if kind == 'industry-by-industry' else figaro_sector_name_mapping_pxp_2022
            self.demand_items = figaro_demand_items
            self.reference = 'https://ec.europa.eu/eurostat/web/products-statistical-working-papers/-/KS-TC-19-002'
            self.contact = 'estat-iga@ec.europa.eu'

            super().__init__()

            pbar.update()
            pbar.set_description('Done')

    @lru_cache()
    def _load_data(self):
        df = pd.read_csv(self._data_file, index_col=0)
        return df

    def _download_data(self):
        import requests

        try:
            r = requests.get(self._url, stream=True)
            with open(self._data_file, "wb") as f:
                for chunk in r.iter_content(1024 * 5):
                    f.write(chunk)
            with open(FILES_LOG, 'a') as files_log:
                files_log.write(db_name + ';' + self._data_file + '\n')
        except Exception as e:
            warn(f"Couldn't download the data. Try downloading manually from {self._url} "
                 f"and save the csv file as {self._file_id}.csv in {DATA_FOLDER}")
            raise e

    @staticmethod
    def remove_downloaded_files(database: str = db_name, verbose: bool = True):
        """Remove downloaded files saved locally

        Args:
            database: Database in lowercase, i.e. all or figaro, exiobase, oecd etc.,
                      default is figaro only
            verbose: Print message that file was removed

        """
        return remove_downloaded_files(database=database, verbose=verbose)
