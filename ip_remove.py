import argparse
import os
import re
import sys
import traceback
from typing import Optional
from typing import Sequence

if sys.version_info < (3, 8):
    import importlib_metadata  # pragma: no cover (>=py38)
else:
    import importlib.metadata as importlib_metadata  # pragma: no cover (<py38)


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
        '--dry-run',
        help='print what would have been done, make no changes',
        action='store_true',
    )
    args = parser.parse_args(argv)

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

    try:
        if args.log_nr:
            filename = os.path.abspath(f'{args.logfile}.{args.log_nr}')
        else:
            filename = os.path.abspath(args.logfile)
        with open(filename, 'r+') as f:
            print(f'\u001b[32mrewriting {filename} ...\u001b[0m')
            content = f.read()
            f.seek(0)
            content_sub = re.sub(IP_PATTERN, '-', content)
            if args.dry_run:
                print('\u001b[33moutput would look like this:\u001b[0m\n')
                print(content_sub)
                print(
                    '\u001b[33mdid not apply any changes (--dry-run)\u001b[0m',
                )
            else:
                f.write(content_sub)
                f.truncate()
                print('\u001b[32mfinished\u001b[0m')
    except Exception as e:
        print(f'\u001b[31m{e}\u001b[0m')
        print(traceback.format_exc())
        raise
    return 0


if __name__ == '__main__':
    exit(main())
