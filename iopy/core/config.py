"""  Created on 08/10/2022::
------------- config -------------
**Authors**: W. Wakker

"""


def _chunk_links(base, chunks):
    """Expand ``{filename: (start_year, end_year)}`` into ``{year: url}``.

    OECD distributes each ICIO edition as a handful of multi-year zip archives
    (e.g. ``2016-2022_SML.zip`` holds one CSV per year), so every year in a range
    resolves to the same download URL.
    """
    return {year: base + filename
            for filename, (start, end) in chunks.items()
            for year in range(start, end + 1)}


config = {
    'oecd':
        {'2021':
             {'links': _chunk_links('https://webfs-sti.oecd.org/files/STI-PIE/ICIO/2021/', {
                  'ICIO2021_1995-1999.zip': (1995, 1999),
                  'ICIO2021_2000-2004.zip': (2000, 2004),
                  'ICIO2021_2005-2009.zip': (2005, 2009),
                  'ICIO2021_2010-2014.zip': (2010, 2014),
                  'ICIO2021_2015-2018.zip': (2015, 2018),
              }),
              'regex_id': r'ICIO2021_[0-9]{4}-[0-9]{4}',
              'num_regions': 71,
              'num_sectors': 45
              },
         '2022-extended':
             {'links': _chunk_links('https://webfs-sti.oecd.org/files/STI-PIE/ICIO/2023/', {
                  '1995-2000_EXT.zip': (1995, 2000),
                  '2001-2005_EXT.zip': (2001, 2005),
                  '2006-2010_EXT.zip': (2006, 2010),
                  '2011-2015_EXT.zip': (2011, 2015),
                  '2016-2020_EXT.zip': (2016, 2020),
              }),
              'regex_id': r'2023/[0-9]{4}-[0-9]{4}_EXT',
              'num_regions': 81,
              'num_sectors': 45},
         '2022-small':
             {'links': _chunk_links('https://webfs-sti.oecd.org/files/STI-PIE/ICIO/2023/', {
                  '1995-2000_SML.zip': (1995, 2000),
                  '2001-2005_SML.zip': (2001, 2005),
                  '2006-2010_SML.zip': (2006, 2010),
                  '2011-2015_SML.zip': (2011, 2015),
                  '2016-2020_SML.zip': (2016, 2020),
              }),
              'regex_id': r'2023/[0-9]{4}-[0-9]{4}_SML',
              'num_regions': 77,
              'num_sectors': 45},
        '2025-extended':
             {'links': _chunk_links('https://webfs-sti.oecd.org/files/STI-PIE/ICIO/2025/', {
                  '1995-2000_EXT.zip': (1995, 2000),
                  '2001-2005_EXT.zip': (2001, 2005),
                  '2006-2010_EXT.zip': (2006, 2010),
                  '2011-2015_EXT.zip': (2011, 2015),
                  '2016-2022_EXT.zip': (2016, 2022),
              }),
              'regex_id': r'2025/[0-9]{4}-[0-9]{4}_EXT',
              'num_regions': 85,
              'num_sectors': 50},
         '2025-regular':
             {'links': _chunk_links('https://webfs-sti.oecd.org/files/STI-PIE/ICIO/2025/', {
                  '1995-2000_SML.zip': (1995, 2000),
                  '2001-2005_SML.zip': (2001, 2005),
                  '2006-2010_SML.zip': (2006, 2010),
                  '2011-2015_SML.zip': (2011, 2015),
                  '2016-2022_SML.zip': (2016, 2022),
              }),
              'regex_id': r'2025/[0-9]{4}-[0-9]{4}_SML',
              'num_regions': 81,
              'num_sectors': 50}

         },

    'figaro':
        {'2022':
            {'links':
                {'product-by-product': {
                    2010: 'https://ec.europa.eu/eurostat/documents/51957/12789261/matrix_eu-ic-io_prod-by-prod_2010.csv/bc2b60d9-32f2-1c80-56e4-f839ca2f06fc?t=1655180575504',
                    2011: 'https://ec.europa.eu/eurostat/documents/51957/12789261/matrix_eu-ic-io_prod-by-prod_2011.csv/74e6f603-1740-116c-3469-4db7ebe97aa2?t=1655182400093',
                    2012: 'https://ec.europa.eu/eurostat/documents/51957/12789261/matrix_eu-ic-io_prod-by-prod_2012.csv/17b1bf95-daa9-a506-9d8b-932edf8f3950?t=1655184005469',
                    2013: 'https://ec.europa.eu/eurostat/documents/51957/12789261/matrix_eu-ic-io_prod-by-prod_2013.csv/d32be770-9f71-e28c-e8ac-11a04d8d885c?t=1655185487140',
                    2014: 'https://ec.europa.eu/eurostat/documents/51957/12789261/matrix_eu-ic-io_prod-by-prod_2014.csv/815e7a8e-a1c7-89f4-e621-ce3971e79c4b?t=1655186769271',
                    2015: 'https://ec.europa.eu/eurostat/documents/51957/12789261/matrix_eu-ic-io_prod-by-prod_2015.csv/3c69e27a-8f45-29e9-cdef-59d8a402e927?t=1655186809149',
                    2016: 'https://ec.europa.eu/eurostat/documents/51957/12789261/matrix_eu-ic-io_prod-by-prod_2016.csv/f82150d8-74b3-b0a3-4764-567eab545b5a?t=1655188856261',
                    2017: 'https://ec.europa.eu/eurostat/documents/51957/12789261/matrix_eu-ic-io_prod-by-prod_2017.csv/7ec909a5-0faa-e45d-2173-43f6c1b59689?t=1655188931368',
                    2018: 'https://ec.europa.eu/eurostat/documents/51957/12789261/matrix_eu-ic-io_prod-by-prod_2018.csv/c44abd15-b354-6690-24dc-f186fe147bb2?t=1655196163454',
                    2019: 'https://ec.europa.eu/eurostat/documents/51957/12789261/matrix_eu-ic-io_prod-by-prod_2019.csv/0ab0c866-8dd8-92d6-1ac7-51ffe78fd5dc?t=1655196217023',
                    2020: 'https://ec.europa.eu/eurostat/documents/51957/12789261/matrix_eu-ic-io_prod-by-prod_2020.csv/3b838d62-884e-c1dc-9693-314b6460af0d?t=1655196273194',
                },
                    'industry-by-industry': {
                        2010: 'https://ec.europa.eu/eurostat/documents/51957/12789261/matrix_eu-ic-io_ind-by-ind_2010.csv/3db6f05f-8343-a45e-2012-14db4607716b?t=1655180547507',
                        2011: 'https://ec.europa.eu/eurostat/documents/51957/12789261/matrix_eu-ic-io_ind-by-ind_2011.csv/5ce2f4ab-f4c1-e1dd-2aac-68813c714414?t=1655182368997',
                        2012: 'https://ec.europa.eu/eurostat/documents/51957/12789261/matrix_eu-ic-io_ind-by-ind_2012.csv/a1ad1f56-3a20-fac1-ee79-9a80b6d25a46?t=1655183982037',
                        2013: 'https://ec.europa.eu/eurostat/documents/51957/12789261/matrix_eu-ic-io_ind-by-ind_2013.csv/eec78482-56e2-053e-5486-15061be568e6?t=1655185412542',
                        2014: 'https://ec.europa.eu/eurostat/documents/51957/12789261/matrix_eu-ic-io_ind-by-ind_2014.csv/35eb67c4-0550-f2ae-b827-6ac240b5f877?t=1655186676930',
                        2015: 'https://ec.europa.eu/eurostat/documents/51957/12789261/matrix_eu-ic-io_ind-by-ind_2015.csv/af93fe1f-a9fd-c094-dd18-a15d390e0f9c?t=1655186725710',
                        2016: 'https://ec.europa.eu/eurostat/documents/51957/12789261/matrix_eu-ic-io_ind-by-ind_2016.csv/8322aa36-8d5c-5d52-07e5-e3d527875d06?t=1655188541728',
                        2017: 'https://ec.europa.eu/eurostat/documents/51957/12789261/matrix_eu-ic-io_ind-by-ind_2017.csv/30ad9b86-689f-d5a1-c80c-6765ea0f5421?t=1655188598849',
                        2018: 'https://ec.europa.eu/eurostat/documents/51957/12789261/matrix_eu-ic-io_ind-by-ind_2018.csv/a0369f43-bf98-a362-9054-f7075cc01704?t=1655195970852',
                        2019: 'https://ec.europa.eu/eurostat/documents/51957/12789261/matrix_eu-ic-io_ind-by-ind_2019.csv/c1354cbb-b3e6-6da5-780a-5be3319ad6d4?t=1655196037947',
                        2020: 'https://ec.europa.eu/eurostat/documents/51957/12789261/matrix_eu-ic-io_ind-by-ind_2020.csv/6dc6df43-0d95-856c-897f-18ba2ca053f1?t=1655196109971',
                    }
                },
                'regex_id': r'[A-Za-z0-9]{8}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{12}',
                'num_regions': 46,
                'num_sectors': 64}
        },
    'exiobase':
        {'3.81':
            {'links':
                {'product-by-product': {
                    1995: 'https://zenodo.org/record/5589597/files/IOT_1995_pxp.zip?download=1',
                    1996: 'https://zenodo.org/record/5589597/files/IOT_1996_pxp.zip?download=1',
                    1997: 'https://zenodo.org/record/5589597/files/IOT_1997_pxp.zip?download=1',
                    1998: 'https://zenodo.org/record/5589597/files/IOT_1998_pxp.zip?download=1',
                    1999: 'https://zenodo.org/record/5589597/files/IOT_1999_pxp.zip?download=1',
                    2000: 'https://zenodo.org/record/5589597/files/IOT_2000_pxp.zip?download=1',
                    2001: 'https://zenodo.org/record/5589597/files/IOT_2001_pxp.zip?download=1',
                    2002: 'https://zenodo.org/record/5589597/files/IOT_2002_pxp.zip?download=1',
                    2003: 'https://zenodo.org/record/5589597/files/IOT_2003_pxp.zip?download=1',
                    2004: 'https://zenodo.org/record/5589597/files/IOT_2004_pxp.zip?download=1',
                    2005: 'https://zenodo.org/record/5589597/files/IOT_2005_pxp.zip?download=1',
                    2006: 'https://zenodo.org/record/5589597/files/IOT_2006_pxp.zip?download=1',
                    2007: 'https://zenodo.org/record/5589597/files/IOT_2007_pxp.zip?download=1',
                    2008: 'https://zenodo.org/record/5589597/files/IOT_2008_pxp.zip?download=1',
                    2009: 'https://zenodo.org/record/5589597/files/IOT_2009_pxp.zip?download=1',
                    2010: 'https://zenodo.org/record/5589597/files/IOT_2010_pxp.zip?download=1',
                    2011: 'https://zenodo.org/record/5589597/files/IOT_2011_pxp.zip?download=1',
                    2012: 'https://zenodo.org/record/5589597/files/IOT_2012_pxp.zip?download=1',
                    2013: 'https://zenodo.org/record/5589597/files/IOT_2013_pxp.zip?download=1',
                    2014: 'https://zenodo.org/record/5589597/files/IOT_2014_pxp.zip?download=1',
                    2015: 'https://zenodo.org/record/5589597/files/IOT_2015_pxp.zip?download=1',
                    2016: 'https://zenodo.org/record/5589597/files/IOT_2016_pxp.zip?download=1',
                    2017: 'https://zenodo.org/record/5589597/files/IOT_2017_pxp.zip?download=1',
                    2018: 'https://zenodo.org/record/5589597/files/IOT_2018_pxp.zip?download=1',
                    2019: 'https://zenodo.org/record/5589597/files/IOT_2019_pxp.zip?download=1',
                    2020: 'https://zenodo.org/record/5589597/files/IOT_2020_pxp.zip?download=1',
                    2021: 'https://zenodo.org/record/5589597/files/IOT_2021_pxp.zip?download=1',
                    2022: 'https://zenodo.org/record/5589597/files/IOT_2022_pxp.zip?download=1',
                },
                    'industry-by-industry': {
                        1995: 'https://zenodo.org/record/5589597/files/IOT_1995_ixi.zip?download=1',
                        1996: 'https://zenodo.org/record/5589597/files/IOT_1996_ixi.zip?download=1',
                        1997: 'https://zenodo.org/record/5589597/files/IOT_1997_ixi.zip?download=1',
                        1998: 'https://zenodo.org/record/5589597/files/IOT_1998_ixi.zip?download=1',
                        1999: 'https://zenodo.org/record/5589597/files/IOT_1999_ixi.zip?download=1',
                        2000: 'https://zenodo.org/record/5589597/files/IOT_2000_ixi.zip?download=1',
                        2001: 'https://zenodo.org/record/5589597/files/IOT_2001_ixi.zip?download=1',
                        2002: 'https://zenodo.org/record/5589597/files/IOT_2002_ixi.zip?download=1',
                        2003: 'https://zenodo.org/record/5589597/files/IOT_2003_ixi.zip?download=1',
                        2004: 'https://zenodo.org/record/5589597/files/IOT_2004_ixi.zip?download=1',
                        2005: 'https://zenodo.org/record/5589597/files/IOT_2005_ixi.zip?download=1',
                        2006: 'https://zenodo.org/record/5589597/files/IOT_2006_ixi.zip?download=1',
                        2007: 'https://zenodo.org/record/5589597/files/IOT_2007_ixi.zip?download=1',
                        2008: 'https://zenodo.org/record/5589597/files/IOT_2008_ixi.zip?download=1',
                        2009: 'https://zenodo.org/record/5589597/files/IOT_2009_ixi.zip?download=1',
                        2010: 'https://zenodo.org/record/5589597/files/IOT_2010_ixi.zip?download=1',
                        2011: 'https://zenodo.org/record/5589597/files/IOT_2011_ixi.zip?download=1',
                        2012: 'https://zenodo.org/record/5589597/files/IOT_2012_ixi.zip?download=1',
                        2013: 'https://zenodo.org/record/5589597/files/IOT_2013_ixi.zip?download=1',
                        2014: 'https://zenodo.org/record/5589597/files/IOT_2014_ixi.zip?download=1',
                        2015: 'https://zenodo.org/record/5589597/files/IOT_2015_ixi.zip?download=1',
                        2016: 'https://zenodo.org/record/5589597/files/IOT_2016_ixi.zip?download=1',
                        2017: 'https://zenodo.org/record/5589597/files/IOT_2017_ixi.zip?download=1',
                        2018: 'https://zenodo.org/record/5589597/files/IOT_2018_ixi.zip?download=1',
                        2019: 'https://zenodo.org/record/5589597/files/IOT_2019_ixi.zip?download=1',
                        2020: 'https://zenodo.org/record/5589597/files/IOT_2020_ixi.zip?download=1',
                        2021: 'https://zenodo.org/record/5589597/files/IOT_2021_ixi.zip?download=1',
                        2022: 'https://zenodo.org/record/5589597/files/IOT_2022_ixi.zip?download=1',
                    }
                },
                'regex_id': r'[A-Z]{3}_[0-9]{4}_[a-z]{3}',
                'num_regions': {'industry-by-industry': 49, 'product-by-product': 49},
                'num_sectors': {'industry-by-industry': 163, 'product-by-product': 200}}
        }
}
