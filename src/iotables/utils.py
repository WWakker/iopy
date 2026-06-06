"""Shared helpers: validation, the downloader, cache cleanup, and country-code maps."""
from iotables.globals import FILES_LOG
from collections import defaultdict
import os


def assert_is_subset(subset, superset):
    if not set(subset).issubset(superset):
        raise ValueError(f'Not found: {set(subset).difference(superset)}')


def download_file(url, dest, proxy=None, verify=True):
    """Stream-download ``url`` to the local path ``dest``.

    Args:
        url: Source URL.
        dest: Local file path to write to.
        proxy: Optional proxy. Either a single URL string (e.g.
               ``'http://user:pass@host:port'``) applied to both http and https,
               or a ``{scheme: url}`` dict passed straight through.
        verify: Verify the server's TLS certificate. Set to ``False`` to skip
                verification (e.g. behind a TLS-intercepting proxy), or pass a
                path to a CA bundle.
    """
    from curl_cffi import requests

    kwargs = {}
    if proxy is not None:
        kwargs['proxies'] = {'http': proxy, 'https': proxy} if isinstance(proxy, str) else proxy

    r = requests.get(url, stream=True, impersonate='chrome', verify=verify, **kwargs)
    if not r.ok:
        raise ConnectionError(r.reason or f'HTTP {r.status_code}')

    # Download to a temporary file and atomically move it into place only once the
    # stream completes, so an interrupted download never leaves a truncated file in
    # the cache (which would otherwise load as a wrong-shaped, silently corrupt matrix).
    tmp = dest + '.part'
    try:
        written = 0
        with open(tmp, 'wb') as f:
            for chunk in r.iter_content():
                f.write(chunk)
                written += len(chunk)

        # Guard against a silently truncated body (server returns 200 then closes the
        # stream early). Only enforce when the server advertised a length and did not
        # transform the bytes -- e.g. CIRCABC serves gzip/chunked with no Content-Length,
        # where the written size legitimately differs from any advertised length.
        content_encoding = (r.headers.get('Content-Encoding') or '').lower()
        expected = r.headers.get('Content-Length')
        if expected is not None and content_encoding in ('', 'identity') and written != int(expected):
            raise ConnectionError(
                f'Incomplete download from {url}: got {written} bytes, expected {expected}')

        os.replace(tmp, dest)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


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
        files = files[database]
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
