import argparse
import os
import re
import sys
import traceback
from typing import NamedTuple
from typing import Optional
from typing import Sequence
from typing import Union


if sys.version_info < (3, 8):  # pragma: no cover (>=py38)
    from typing_extensions import Literal
    import importlib_metadata
else:  # pragma: no cover (<py38)
    from typing import Literal
    import importlib.metadata as importlib_metadata


IP_PATTERN = re.compile(
    # ipv4
    r'((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|'
    r'1{0,1}[0-9]){0,1}[0-9])|'
    # ipv6
    r'((([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:'
    r'|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}'
    r'(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4})'
    r'{1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|'
    r'([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|'
    r'[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|'
    r':((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}'
    r'%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|'
    r'1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|'
    r'1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|'
    r'1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|'
    r'1{0,1}[0-9]){0,1}[0-9])))',
)


class IpAdress(NamedTuple):
    address: str
    kind: Union[Literal['ipv4'], Literal['ipv6']]


def _ip_type(ip: str) -> Union[Literal['ipv4'], Literal['ipv6']]:
    if ':' in ip:
        return 'ipv6'
    elif '.' in ip:
        return 'ipv4'
    else:
        raise TypeError


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog='ip-remove',
        description='remove ipv4 and ipv6 addresses from a file',
    )
    parser.add_argument(
        '-V', '--version',
        action='version',
        version=f'%(prog)s {importlib_metadata.version("ip-remove")}',
    )
    parser.add_argument('logfile', help='path to logfile', type=str)
    parser.add_argument(
        '--log-nr',
        help='number of the log to change e.g. foo.log.1',
        type=int,
    )
    parser.add_argument(
        '--anonymize',
        help='anonymize the ip address by replacing the last n octets with 0',
        nargs='?',
        const=1,
        type=int,
    )
    parser.add_argument(
        '--dry-run',
        help='print what would have been done, make no changes',
        action='store_true',
    )
    args = parser.parse_args(argv)

    try:
        if args.log_nr:
            filename = os.path.abspath(f'{args.logfile}.{args.log_nr}')
        else:
            filename = os.path.abspath(args.logfile)
        with open(filename, 'r+') as f:
            print(f'\u001b[32mrewriting {filename} ...\u001b[0m')
            content = f.read()
            if args.anonymize is not None:
                if args.anonymize > 4:
                    print(
                        '\u001b[33mWARNING: anonymize is set larger than 4. '
                        'IPv4 will be rewritten to 0.0.0.0\u001b[0m',
                    )
                if args.anonymize > 8:
                    print(
                        '\u001b[33mWARNING: anonymize is set larger than 8. '
                        'IPv6 will be rewritten to 0.0.0.0.0.0.0.0\u001b[0m',
                    )
                sub_ips = {
                    IpAdress(i.group(), _ip_type(i.group()))
                    for i in re.finditer(IP_PATTERN, content)
                }
                for ip in sub_ips:
                    if ip.kind == 'ipv6':
                        octets = re.split(':', ip.address)
                    else:
                        octets = re.split(r'\.', ip.address)
                    # exclude `::` this way
                    if len(octets) > 1 and '' not in octets:
                        for i in range(1, args.anonymize + 1):
                            # max len of ipv4
                            if ip.kind == 'ipv4' and i > 4:
                                break
                            # max len of ipv6
                            if ip.kind == 'ipv6' and i > 8:
                                break
                            octets[i * -1] = '0'
                        if ip.kind == 'ipv6':
                            ip_sub = ':'.join(octets)
                        else:
                            ip_sub = '.'.join(octets)
                        content = re.sub(ip.address, ip_sub, content)
            else:
                content = re.sub(IP_PATTERN, '-', content)
            if args.dry_run:
                print('\u001b[33moutput would look like this:\u001b[0m\n')
                print(content)
                print(
                    '\u001b[33mdid not apply any changes (--dry-run)\u001b[0m',
                )
            else:
                f.seek(0)
                f.write(content)
                f.truncate()
                print('\u001b[32mfinished\u001b[0m')
    except Exception as e:
        print(f'\u001b[31m{e}\u001b[0m')
        print(traceback.format_exc())
        raise
    return 0


if __name__ == '__main__':
    exit(main())
