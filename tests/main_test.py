import pytest

from ip_remove import _ip_type
from ip_remove import main


@pytest.fixture()
def test_file(tmpdir):
    def _create_dummy_file(contents):
        f = tmpdir.join('test.log')
        f.write(contents)
        return f
    return _create_dummy_file


def test_show_help():
    with pytest.raises(SystemExit):
        main(['--help'])


def test_show_version():
    with pytest.raises(SystemExit):
        main(['--version'])


def test_dry_run(test_file):
    test_str = 'foo,bar,10.20.30.40,baz\n'
    f = test_file(test_str)
    main([str(f), '--dry-run'])
    with open(f) as x:
        assert x.read() == test_str


@pytest.mark.parametrize(
    'ip',
    (
        '1.2.3.4',
        '0.0.0.0',
        '255.255.255.255',
        '::',
        '192.168.2.1',
    ),
)
def test_replace_ipv4(ip, test_file):
    f = test_file(ip)
    main([str(f)])
    with open(f) as x:
        assert x.read() == '-'


@pytest.mark.parametrize(
    'ip',
    (
        'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff',
        '2001:0db8:85a3:08d3:1319:8a2e:0370:7344',
    ),
)
def test_replace_ipv6(ip, test_file):
    f = test_file(ip)
    main([str(f)])
    with open(f) as x:
        assert x.read() == '-'


def test_specific_log_nr(tmpdir):
    f = tmpdir.join('test.log.7')
    f.write('foo,1.2.3.4,bar\n')
    main([str(f)[:-2], '--log-nr', '7'])
    with open(f) as x:
        assert x.read() == 'foo,-,bar\n'


def test_error_file_not_found():
    with pytest.raises(Exception):
        main(['not_existing_file.log'])


@pytest.mark.parametrize(
    ('ip', 'exp'),
    (
        ('1.2.3.4', '1.2.3.0'),
        ('0.0.0.0', '0.0.0.0'),
        ('255.255.255.255', '255.255.255.0'),
        ('::', '::'),
        ('192.168.2.1', '192.168.2.0'),
    ),
)
def test_anonymize_ipv4_default(ip, exp, test_file):
    f = test_file(ip)
    main([str(f), '--anonymize'])
    with open(f) as x:
        assert x.read() == exp


@pytest.mark.parametrize(
    ('ip', 'exp'),
    (
        ('1.2.3.4', '1.2.0.0'),
        ('0.0.0.0', '0.0.0.0'),
        ('255.255.255.255', '255.255.0.0'),
        ('::', '::'),
        ('192.168.2.1', '192.168.0.0'),
    ),
)
def test_anonymize_ipv4_multiple_digits(ip, exp, test_file):
    f = test_file(ip)
    main([str(f), '--anonymize', '2'])
    with open(f) as x:
        assert x.read() == exp


@pytest.mark.parametrize(
    ('ip', 'exp'),
    (
        (
            'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff',
            'ffff:ffff:ffff:ffff:ffff:ffff:ffff:0',
        ),
        (
            '2001:0db8:85a3:08d3:1319:8a2e:0370:7344',
            '2001:0db8:85a3:08d3:1319:8a2e:0370:0',
        ),
    ),
)
def test_anonymize_ipv6_default(ip, exp, test_file):
    f = test_file(ip)
    main([str(f), '--anonymize'])
    with open(f) as x:
        assert x.read() == exp


@pytest.mark.parametrize(
    ('ip', 'exp'),
    (
        (
            'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff',
            'ffff:ffff:ffff:ffff:ffff:ffff:0:0',
        ),
        (
            '2001:0db8:85a3:08d3:1319:8a2e:0370:7344',
            '2001:0db8:85a3:08d3:1319:8a2e:0:0',
        ),
    ),
)
def test_anonymize_ipv6_multiple_digits(ip, exp, test_file):
    f = test_file(ip)
    main([str(f), '--anonymize', '2'])
    with open(f) as x:
        assert x.read() == exp


@pytest.mark.parametrize(
    ('ip', 'exp'),
    (
        ('ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff', '0:0:0:0:0:0:0:0'),
        ('2001:0db8:85a3:08d3:1319:8a2e:0370:7344', '0:0:0:0:0:0:0:0'),
        ('1.2.3.4', '0.0.0.0'),
        ('0.0.0.0', '0.0.0.0'),
        ('255.255.255.255', '0.0.0.0'),
        ('::', '::'),
        ('192.168.2.1', '0.0.0.0'),
    ),
)
def test_anonymize_too_many_digits(ip, exp, test_file, capsys):
    f = test_file(ip)
    main([str(f), '--anonymize', '25'])
    with open(f) as x:
        assert x.read() == exp
    captured = capsys.readouterr()
    assert (
        '\u001b[33mWARNING: anonymize is set larger than 4. '
        'IPv4 will be rewritten to 0.0.0.0\u001b[0m\n'
    ) in captured.out
    assert (
        '\u001b[33mWARNING: anonymize is set larger than 8. '
        'IPv6 will be rewritten to 0:0:0:0:0:0:0:0\u001b[0m\n'
    ) in captured.out


@pytest.mark.parametrize(
    ('ip', 'exp'),
    (
        ('1.2.3.4', 'ipv4'),
        ('ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff', 'ipv6'),
    ),
)
def test_ip_type(ip, exp):
    assert _ip_type(ip) == exp


def test_ip_type_invalid():
    with pytest.raises(TypeError):
        _ip_type('foobar')
