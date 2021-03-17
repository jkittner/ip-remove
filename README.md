[![ci](https://github.com/theendlessriver13/ip-remove/workflows/ci/badge.svg)](https://github.com/theendlessriver13/ip-remove/actions?query=workflow%3Aci)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/theendlessriver13/ip-remove/master.svg)](https://results.pre-commit.ci/latest/github/theendlessriver13/ip-remove/master)
[![codecov](https://codecov.io/gh/theendlessriver13/ip-remove/branch/master/graph/badge.svg)](https://codecov.io/gh/theendlessriver13/ip-remove)

# ip-remove

ip-remove removes ipv4 and ipv6 addresses from a file. This can be useful when IP-addresses must not be stored longer than n days for data protection reasons, but you still want to keep the logs for a longer time period.

### installation

```bash
pip install git+https://github.com/theendlessriver13/ip-remove.git@master
```

### Usage

```console
usage: ip-remove [-h] [-V] [--log-nr LOG_NR] [--anonymize [ANONYMIZE]] [--dry-run] logfile

remove ipv4 and ipv6 addresses from a file

positional arguments:
  logfile               path to logfile

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  --log-nr LOG_NR       number of the log to change e.g. foo.log.1
  --anonymize [ANONYMIZE]
                        anonymize the ip address by replacing the last n octets with 0
  --dry-run             print what would have been done, make no changes
```

- remove the ip from `foo.txt`: `ip-remove foo.txt`
- test with a dry run first `ip-remove foo.txt --dry-run` and get the output to stdout without modifying the file
- use `ip-remove foo.txt --anonymize 2` to replace the last two digits of the IP address

### Usage with `logrotate`

This tool can be used as a `postrotate` script with `logrotate`.

example config:

```console
/var/log/foo/*.log {
    daily
    missingok
    rotate 14
    copytruncate
    postrotate
        /home/runner/venv/bin/ip-remove $1 --log-nr 7
    endscript
}
```

- you can specify `--log-nr 7` to only remove the ip addresses from the 7th rotated log (e.g. in `logrotate` after seven days when using `daily`)
- the script is run on all logs the `logrotate` config covers when rotating e.g. in this case `access.log` and `error.log` would be processed
- the operation is **not** atomic!
