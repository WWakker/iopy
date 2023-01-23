"""  Created on 11/10/2022::
------------- utils -------------
**Authors**: W. Wakker

"""
from iopy.core.globals import FILES_LOG
from collections import defaultdict
import os


def assert_is_subset(subset, superset):
    if not set(subset).issubset(superset):
        raise ValueError(f'Not found: {set(subset).difference(superset)}')


def replace_if_exists(x, mapping):
    """Replace if x exists in mapping, otherwise return x

    Args:
        x: Input
        mapping: Mapping

    Returns:
        x
    """
    if x in mapping:
        return mapping[x]
    return x


def remove_downloaded_files(database: str = 'all',
                            verbose: bool = True):
    """Remove downloaded files saved locally

    Args:
        database: Database in lowercase, i.e. all or figaro, exiobase, oecd etc.,
                  default is to remove files from all databases
        verbose: Print message that file was removed

    """
    if not os.path.exists(FILES_LOG):
        print('No files to remove')
        return
    files = defaultdict(set)
    with open(FILES_LOG, 'r') as files_log:
        for line in files_log:
            db, file = line.split(';')
            file = file.rstrip('\n')
            files[db].update({file})
    other_files = {}
    if database != 'all':
        if database not in files:
            print(f'no files found for {database}, only for {list(files.keys())}')
            return
        other_files = {k: v for k, v in files.items() if k != database}
        files = files[db]
    else:
        files = {item for sublist in files.values() for item in sublist}
    for path in files:
        os.remove(path)
        if verbose:
            print(f'Removed {path}')

    os.remove(FILES_LOG)

    if database != 'all':
        if other_files:
            with open(FILES_LOG, 'w') as files_log:
                for db in other_files.keys():
                    for path in other_files[db]:
                        files_log.write(db + ';' + path + '\n')


ALPHA3_TO_ALPHA2 = {'AND': 'AD', 'ARE': 'AE', 'AFG': 'AF', 'ATG': 'AG', 'AIA': 'AI', 'ALB': 'AL', 'ARM': 'AM',
                    'AGO': 'AO', 'ATA': 'AQ', 'ARG': 'AR', 'ASM': 'AS', 'AUT': 'AT', 'AUS': 'AU', 'ABW': 'AW',
                    'ALA': 'AX', 'AZE': 'AZ', 'BIH': 'BA', 'BRB': 'BB', 'BGD': 'BD', 'BEL': 'BE', 'BFA': 'BF',
                    'BGR': 'BG', 'BHR': 'BH', 'BDI': 'BI', 'BEN': 'BJ', 'BLM': 'BL', 'BMU': 'BM', 'BRN': 'BN',
                    'BOL': 'BO', 'BES': 'BQ', 'BRA': 'BR', 'BHS': 'BS', 'BTN': 'BT', 'BVT': 'BV', 'BWA': 'BW',
                    'BLR': 'BY', 'BLZ': 'BZ', 'CAN': 'CA', 'CCK': 'CC', 'COD': 'CD', 'CAF': 'CF', 'COG': 'CG',
                    'CHE': 'CH', 'CIV': 'CI', 'COK': 'CK', 'CHL': 'CL', 'CMR': 'CM', 'CHN': 'CN', 'COL': 'CO',
                    'CRI': 'CR', 'CUB': 'CU', 'CPV': 'CV', 'CUW': 'CW', 'CXR': 'CX', 'CYP': 'CY', 'CZE': 'CZ',
                    'DEU': 'DE', 'DJI': 'DJ', 'DNK': 'DK', 'DMA': 'DM', 'DOM': 'DO', 'DZA': 'DZ', 'ECU': 'EC',
                    'EST': 'EE', 'EGY': 'EG', 'ESH': 'EH', 'ERI': 'ER', 'ESP': 'ES', 'ETH': 'ET', 'FIN': 'FI',
                    'FJI': 'FJ', 'FLK': 'FK', 'FSM': 'FM', 'FRO': 'FO', 'FRA': 'FR', 'GAB': 'GA', 'GBR': 'GB',
                    'GRD': 'GD', 'GEO': 'GE', 'GUF': 'GF', 'GGY': 'GG', 'GHA': 'GH', 'GIB': 'GI', 'GRL': 'GL',
                    'GMB': 'GM', 'GIN': 'GN', 'GLP': 'GP', 'GNQ': 'GQ', 'GRC': 'GR', 'SGS': 'GS', 'GTM': 'GT',
                    'GUM': 'GU', 'GNB': 'GW', 'GUY': 'GY', 'HKG': 'HK', 'HMD': 'HM', 'HND': 'HN', 'HRV': 'HR',
                    'HTI': 'HT', 'HUN': 'HU', 'IDN': 'ID', 'IRL': 'IE', 'ISR': 'IL', 'IMN': 'IM', 'IND': 'IN',
                    'IOT': 'IO', 'IRQ': 'IQ', 'IRN': 'IR', 'ISL': 'IS', 'ITA': 'IT', 'JEY': 'JE', 'JAM': 'JM',
                    'JOR': 'JO', 'JPN': 'JP', 'KEN': 'KE', 'KGZ': 'KG', 'KHM': 'KH', 'KIR': 'KI', 'COM': 'KM',
                    'KNA': 'KN', 'PRK': 'KP', 'KOR': 'KR', 'KWT': 'KW', 'CYM': 'KY', 'KAZ': 'KZ', 'LAO': 'LA',
                    'LBN': 'LB', 'LCA': 'LC', 'LIE': 'LI', 'LKA': 'LK', 'LBR': 'LR', 'LSO': 'LS', 'LTU': 'LT',
                    'LUX': 'LU', 'LVA': 'LV', 'LBY': 'LY', 'MAR': 'MA', 'MCO': 'MC', 'MDA': 'MD', 'MNE': 'ME',
                    'MAF': 'MF', 'MDG': 'MG', 'MHL': 'MH', 'MKD': 'MK', 'MLI': 'ML', 'MMR': 'MM', 'MNG': 'MN',
                    'MAC': 'MO', 'MNP': 'MP', 'MTQ': 'MQ', 'MRT': 'MR', 'MSR': 'MS', 'MLT': 'MT', 'MUS': 'MU',
                    'MDV': 'MV', 'MWI': 'MW', 'MEX': 'MX', 'MYS': 'MY', 'MOZ': 'MZ', 'NAM': 'NA', 'NCL': 'NC',
                    'NER': 'NE', 'NFK': 'NF', 'NGA': 'NG', 'NIC': 'NI', 'NLD': 'NL', 'NOR': 'NO', 'NPL': 'NP',
                    'NRU': 'NR', 'NIU': 'NU', 'NZL': 'NZ', 'OMN': 'OM', 'PAN': 'PA', 'PER': 'PE', 'PYF': 'PF',
                    'PNG': 'PG', 'PHL': 'PH', 'PAK': 'PK', 'POL': 'PL', 'SPM': 'PM', 'PCN': 'PN', 'PRI': 'PR',
                    'PSE': 'PS', 'PRT': 'PT', 'PLW': 'PW', 'PRY': 'PY', 'QAT': 'QA', 'REU': 'RE', 'ROU': 'RO',
                    'SRB': 'RS', 'RUS': 'RU', 'RWA': 'RW', 'SAU': 'SA', 'SLB': 'SB', 'SYC': 'SC', 'SDN': 'SD',
                    'SWE': 'SE', 'SGP': 'SG', 'SHN': 'SH', 'SVN': 'SI', 'SJM': 'SJ', 'SVK': 'SK', 'SLE': 'SL',
                    'SMR': 'SM', 'SEN': 'SN', 'SOM': 'SO', 'SUR': 'SR', 'SSD': 'SS', 'STP': 'ST', 'SLV': 'SV',
                    'SXM': 'SX', 'SYR': 'SY', 'SWZ': 'SZ', 'TCA': 'TC', 'TCD': 'TD', 'ATF': 'TF', 'TGO': 'TG',
                    'THA': 'TH', 'TJK': 'TJ', 'TKL': 'TK', 'TLS': 'TL', 'TKM': 'TM', 'TUN': 'TN', 'TON': 'TO',
                    'TUR': 'TR', 'TTO': 'TT', 'TUV': 'TV', 'TWN': 'TW', 'TZA': 'TZ', 'UKR': 'UA', 'UGA': 'UG',
                    'UMI': 'UM', 'USA': 'US', 'URY': 'UY', 'UZB': 'UZ', 'VAT': 'VA', 'VCT': 'VC', 'VEN': 'VE',
                    'VGB': 'VG', 'VIR': 'VI', 'VNM': 'VN', 'VUT': 'VU', 'WLF': 'WF', 'WSM': 'WS', 'YEM': 'YE',
                    'MYT': 'YT', 'ZAF': 'ZA', 'ZMB': 'ZM', 'ZWE': 'ZW'}
