"""  Created on 15/11/2022::
------------- exiobase -------------
**Authors**: S. Boldrini
"""

from iopy.core.matrix import Matrix
from functools import lru_cache
import numpy as np
import pandas as pd
from tqdm import tqdm
from zipfile import ZipFile
import re
import os
from iopy.core.config import config
from iopy.core.base_io import IO
from warnings import warn
from iopy.core.globals import DATA_FOLDER, FILES_LOG
from iopy.core.utils import remove_downloaded_files

db_name = os.path.basename(__file__).rstrip('.py')


def process_df(df):
    return (df,
            df.index.tolist(),
            df.columns.tolist())


class ExioBase(IO):
    """Class to load and work with ExioBase input-output data"""

    def __init__(self,
                 version: str,
                 year: int,
                 kind: str = 'industry-by-industry',
                 refresh: bool = False):
        """

        Args:
            version: Edition, e.g. '3.81' (default)
            year: Year from 1995 to 2022
            kind: industry-by-industry (default) or product-by-product
            refresh: Download the data even if it exists on the hard drive
        """

        assert kind in {'industry-by-industry', 'product-by-product'}

        if version not in config['exiobase'].keys():
            raise ValueError(
                f"Version selected not recognized. \n Please choose among {list(config['exiobase'].keys())}")

        if year not in config['exiobase'][version]['links'][kind].keys():
            raise ValueError(
                f"Year selected not present in the {version} version. \n "
                f"Please choose among {list(config['exiobase'][version]['links'][kind].keys())} or consider changing version.")

        self.version = version
        self.year = year
        self.kind = kind
        self._url = config['exiobase'][version]['links'][kind][year]
        self._file_id = re.search(config['exiobase'][version]['regex_id'], self._url).group(0)
        self._data_file = os.path.join(DATA_FOLDER, self._file_id + '.zip')
        file_exists = os.path.isfile(self._data_file)
        download = not file_exists or refresh
        with tqdm(total=3 if download else 2) as pbar:
            # Download
            if download:
                pbar.set_description('Downloading data...')
                self._download_data()
                pbar.update()

            # Load
            pbar.set_description('Loading data...')
            self.df = None
            self._Z_raw, self._FD_raw, self._X_raw, self._metadata, self._sector_codes, self._FD_codes = self._load_data()

            exiobase_sector_name_mapping = self._sector_codes.reset_index().set_index('CodeNr')['Name'].to_dict()
            exiobase_FD_name_mapping = self._FD_codes.reset_index().set_index('CodeNr')['Name'].to_dict()

            # Convert sector names in sector codes for Z
            self._Z_raw.index = self._Z_raw.index.set_levels(
                self._Z_raw.index.levels[1].map(self._sector_codes['CodeNr'].to_dict()), level=1)
            self._Z_raw.columns = self._Z_raw.columns.set_levels(
                self._Z_raw.columns.levels[1].map(self._sector_codes['CodeNr'].to_dict()), level=1)

            # Convert sector names in sector codes for FD
            self._FD_raw.index = self._FD_raw.index.set_levels(
                self._FD_raw.index.levels[1].map(self._sector_codes['CodeNr'].to_dict()), level=1)
            self._FD_raw.columns = self._FD_raw.columns.set_levels(
                self._FD_raw.columns.levels[1].map(self._FD_codes['CodeNr'].to_dict()), level=1)

            pbar.update()

            # Create matrices
            pbar.set_description('Creating matrices...')
            assert self._Z_raw.shape[0] == self._Z_raw.shape[1]
            self.rs = config['exiobase'][version]['num_regions'][kind] * config['exiobase'][version]['num_sectors'][kind]
            self.Z = Matrix('Intermediate use',
                            *process_df(self._Z_raw))
            self.FD_GRAN = Matrix('Final demand granular',
                             *process_df(self._FD_raw))
            self.FD = Matrix('Final demand',
                             self.FD_GRAN.sum(1).reshape(-1, 1),
                             rows=self.Z.rows,
                             columns=['FD'])
            self.X = Matrix('Output',
                            self._X_raw.iloc[:, [-1]],
                            rows=self.Z.rows,
                            columns=['X'])
            self.V = Matrix('GVA',
                            (self.X.flatten() - self.Z.sum(0).flatten()).reshape(1, len(self.X)),
                            rows=['GVA'],
                            columns=self.Z.columns)

            self.ADD = {}

            # Create country level FD
            fd_region = pd.DataFrame(self.FD_GRAN,
                                     columns=[r for r, s in self.FD_GRAN.columns]).T
            fd_region.index.name = 'region'

            self.FD_REGION = Matrix('Final demand by region',
                                    fd_region.groupby('region').sum(0).T,
                                    rows=self.Z.rows,
                                    columns=fd_region.groupby('region').sum(0).T.columns.to_list())

            self.regions = list(sorted(np.unique([r for r, s in self.Z.rows])))
            self.sectors = list(sorted(np.unique([s for r, s in self.Z.rows])))
            self.unit = 'Million EUR'
            self.sector_name_mapping = exiobase_sector_name_mapping
            self.demand_items = exiobase_FD_name_mapping
            self.reference = 'EXIOBASE3'
            self.contact = 'https://www.exiobase.eu/index.php/about-us/contact-us'
            super().__init__()

            pbar.update()
            pbar.set_description('Done')

    @lru_cache()
    def _load_data(self):
        folder = f'IOT_{self.year}_{"ixi" if self.kind == "industry-by-industry" else "pxp"}'
        with ZipFile(self._data_file, 'r') as zf:
            with zf.open(f'{folder}/Z.txt', 'r') as txt_file:
                z_raw = pd.read_csv(txt_file,
                                    header=[0, 1],
                                    index_col=[0, 1],
                                    sep='\t')

            with zf.open(f'{folder}/Y.txt', 'r') as txt_file:
                fd_raw = pd.read_csv(txt_file,
                                     header=[0, 1],
                                     index_col=[0, 1],
                                     sep='\t')

            with zf.open(f'{folder}/x.txt', 'r') as txt_file:
                x_raw = pd.read_csv(txt_file,
                                    sep='\t',
                                    index_col=[0, 1])

            sector_file = 'industries' if self.kind == 'industry-by-industry' else 'products'
            with zf.open(f'{folder}/{sector_file}.txt', 'r') as csv_file:
                sector_codes = pd.read_csv(csv_file, sep='\t', index_col=1)

            with zf.open(f'{folder}/finaldemands.txt', 'r') as csv_file:
                FD_codes = pd.read_csv(csv_file, sep='\t', index_col=1)

            with zf.open(f'{folder}/metadata.json', 'r') as json_file:
                metadata = pd.read_json(json_file)

        return z_raw, fd_raw, x_raw, metadata, sector_codes, FD_codes

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
                 f"and save the csv file as {self._file_id}.csv in {self._data_folder}")
            raise e

    @staticmethod
    def remove_downloaded_files(database: str = db_name, verbose: bool = True):
        """Remove downloaded files saved locally

        Args:
            database: Database in lowercase, i.e. all or figaro, exiobase, oecd etc.,
                      default is exiobase only
            verbose: Print message that file was removed

        """
        return remove_downloaded_files(database=database, verbose=verbose)
