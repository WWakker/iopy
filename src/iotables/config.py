"""Single source of truth for the data that exists: download links and shapes per database."""


def _chunk_links(base, chunks):
    """Expand ``{filename: (start_year, end_year)}`` into ``{year: url}``.

    OECD distributes each ICIO edition as a handful of multi-year zip archives
    (e.g. ``2016-2022_SML.zip`` holds one CSV per year), so every year in a range
    resolves to the same download URL.
    """
    return {year: base + filename
            for filename, (start, end) in chunks.items()
            for year in range(start, end + 1)}


def _circabc_links(kind_tag, ids):
    """Build CIRCABC anonymous download URLs for Figaro from ``{year: node_id}``.

    Eurostat distributes the Figaro 2025 edition through CIRCABC; every file has a
    stable, auth-free download URL of the form ``/sd/a/{node_id}/{filename}``.
    """
    return {year: f'https://circabc.europa.eu/sd/a/{nid}/matrix_eu-ic-io_{kind_tag}_25ed_{year}.csv'
            for year, nid in ids.items()}


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
        {
         '2025':
             {'links':
                  {'product-by-product': _circabc_links('prod-by-prod', {
                  2010: 'f6d2007e-34c9-420a-a106-8c5ea836c49d',
                  2011: 'd27f7d7c-4006-4c36-8820-7d9990679323',
                  2012: '7cea8b73-f166-47ff-9c27-f240794b57af',
                  2013: 'd56c2ed9-0c4f-40a3-9bbc-1aee49f5bd45',
                  2014: 'b5aa0e38-3d1b-496b-b180-bbd9bab3e153',
                  2015: 'd037b772-8bf9-424f-97a4-9274d261e6cf',
                  2016: '66369d21-8262-47d6-ad8a-dc536a2466d0',
                  2017: 'd6848c38-9569-4848-bb68-4144fed38c71',
                  2018: '557b9483-023e-497c-96c5-44ce807bd444',
                  2019: 'fa0e9127-7a2b-4b74-bbad-1bc9e717197b',
                  2020: '46f5665e-d2e1-4270-95a1-970da3d70d32',
                  2021: 'a7e2919d-f084-4c35-8b21-e960a854e2bd',
                  2022: '31484cee-43fe-45d4-a546-209e5898c6dd',
                  2023: 'e213892a-afac-4d34-83e9-45e8a324e7e8',
                  }),
                   'industry-by-industry': _circabc_links('ind-by-ind', {
                  2010: 'fc80f855-d144-476e-b4bf-5cfba946819c',
                  2011: '1bcb2624-04ed-43e1-8588-df6680ed352a',
                  2012: '399671ad-cbb3-493e-ad5f-83e989f1eecc',
                  2013: 'a2b4746d-1d11-4a44-ab1c-50ac956f0849',
                  2014: 'beba57b2-2696-497a-b92f-2a5beca724c7',
                  2015: '1a194b8c-6ea1-4bec-9c73-0cd599febcc3',
                  2016: '2cdd74fc-0bce-4ae0-8bf2-34d34546d86d',
                  2017: '4a11c796-4186-4cce-a02f-12d353fc5e59',
                  2018: '7a57a374-2200-498c-bb5f-cee24202b0b8',
                  2019: 'c3467617-8a00-44a0-9b6b-ccad8a2ab58d',
                  2020: '4df668e1-2a8a-4e84-ae57-00309d8bc760',
                  2021: '6736dea8-da14-450f-b212-a791baf238c8',
                  2022: 'b20c339d-984f-413c-a499-54ff76beb90c',
                  2023: '21557f49-1e94-431c-8523-d972fec020b8',
                  })},
              'regex_id': r'matrix_eu-ic-io_[a-z-]+_25ed_[0-9]{4}',
              'num_regions': 50,
              'num_sectors': 64},
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
