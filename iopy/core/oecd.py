"""  Created on 06/09/2022::
------------- oecd -------------
**Authors**: W. Wakker

"""
from iopy.core.mappings import oecd_sector_name_mapping, oecd_demand_items, oecd_sector_2022_2021_mapping
from iopy.core.matrix import Matrix
from functools import lru_cache
import numpy as np
import pandas as pd
from iopy.core.utils import ALPHA3_TO_ALPHA2
from tqdm import tqdm
from zipfile import ZipFile
import re
import os
from iopy.core.config import config
from iopy.core.base_io import IO
from iopy.core.utils import replace_if_exists, remove_downloaded_files
from iopy.core.globals import DATA_FOLDER, FILES_LOG
from warnings import warn
from functools import partial

db_name = os.path.basename(__file__).rstrip('.py')


def process_df(df):
    if df.shape[0] > 1 and df.shape[1] > 1:
        return (df,
                [(ALPHA3_TO_ALPHA2[r] if r in ALPHA3_TO_ALPHA2 else r, s) for r, s in df.index.str.split('_')],
                [(ALPHA3_TO_ALPHA2[r] if r in ALPHA3_TO_ALPHA2 else r, s) for r, s in df.columns.str.split('_')])
    elif df.shape[0] == 1:
        return (df,
                df.index.to_list(),
                [(ALPHA3_TO_ALPHA2[r] if r in ALPHA3_TO_ALPHA2 else r, s) for r, s in df.columns.str.split('_')])
    else:
        return (df,
                [(ALPHA3_TO_ALPHA2[r] if r in ALPHA3_TO_ALPHA2 else r, s) for r, s in df.index.str.split('_')],
                df.columns.to_list())


class OECD(IO):
    """Class to load and work with OECD input-output data"""

    def __init__(self,
                 version: str,
                 year: int,
                 refresh: bool = False):
        """

        Args:
            version: Publication version of the data; '2021', '2022-small' or '2022-extended'
            year: Year
            refresh: Download the data even if it exists on the hard drive
        """

        if version not in config['oecd'].keys():
            raise ValueError(
                f"Version selected not recognized. \n Please choose among {list(config['oecd'].keys())}")

        if year not in config['oecd'][version]['links'].keys():
            raise ValueError(
                f"Year selected not present in the {version} version. \n "
                f"Please choose among {list(config['oecd'][version]['links'].keys())} or consider changing version.")

        self.year = year
        self.version = version
        self._url = config['oecd'][version]['links'][year]
        self._file_id = re.search(config['oecd'][version]['regex_id'], self._url).group(0)
        self._data_file = os.path.join(DATA_FOLDER, self._file_id + '.zip')
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

            if version in ['2022-small', '2022-extended']:
                self.df.columns = self.df.columns.str[:4] + self.df.columns.str[4:].map(
                    partial(replace_if_exists, mapping=oecd_sector_2022_2021_mapping))
                self.df.index = self.df.index.str[:4] + self.df.index.str[4:].map(
                    partial(replace_if_exists, mapping=oecd_sector_2022_2021_mapping))

            # Create matrices
            pbar.set_description('Creating matrices...')
            self.rs = config['oecd'][version]['num_regions'] * config['oecd'][version]['num_sectors']
            self.Z = Matrix('Intermediate use',
                            *process_df(self.df.iloc[:self.rs, :self.rs]))
            self.FD_GRAN = Matrix('Final demand granular',
                                  *process_df(self.df.iloc[:self.rs, self.rs:-1]))
            self.FD = Matrix('Final demand',
                             self.FD_GRAN.sum(1).reshape(-1, 1),
                             rows=self.Z.rows,
                             columns=['FD'])
            self.X = Matrix('Output',
                            self.df.iloc[:self.rs, [-1]],
                            rows=self.Z.rows,
                            columns=['X'])
            self.V = Matrix('GVA',
                            (self.X.flatten() - self.Z.sum(0).flatten()).reshape(1, len(self.X)),
                            rows=['GVA'],
                            columns=self.Z.columns)
            VA = Matrix('Value added at basic prices (net)',
                        *process_df(
                            self.df.iloc[[self.df.index.get_loc('VALU' if version == '2021' else 'VA')], :self.rs]))

            TLS = Matrix('Taxes less subsidies on intermediate and final products',
                         *process_df(self.df.iloc[self.rs:-2, :-1]))

            self.ADD = {'VA': VA,
                        'TLS': TLS}

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
            self.unit = 'Million USD'
            self.sector_name_mapping = oecd_sector_name_mapping
            self.demand_items = oecd_demand_items
            self.reference = f'OECD ({self.version[:4]}), OECD Inter-Country Input-Output Database, http://oe.cd/icio'
            self.contact = 'ICIO-TiVA.Contact@oecd.org, mentioning ICIO'

            super().__init__()

            pbar.update()
            pbar.set_description('Done')

    @lru_cache()
    def _load_data(self):
        if self.version == '2021':
            filename = f'ICIO2021_{self.year}.csv'
        elif self.version == '2022-extended':
            filename = f'{self.year}.CSV'
        elif self.version == '2022-small':
            filename = f'{self.year}SML.CSV'
        with ZipFile(self._data_file, 'r') as zf:
            with zf.open(filename, 'r') as csv_file:
                df = pd.read_csv(csv_file, index_col=0)
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
                 f"and save the zip file as {self._file_id}.zip in {DATA_FOLDER}")
            raise e

    @staticmethod
    def remove_downloaded_files(database: str = db_name, verbose: bool = True):
        """Remove downloaded files saved locally

        Args:
            database: Database in lowercase, i.e. all or figaro, exiobase, oecd etc.,
                      default is oecd only
            verbose: Print message that file was removed

        """
        return remove_downloaded_files(database=database, verbose=verbose)
