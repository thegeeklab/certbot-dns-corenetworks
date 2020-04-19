# certbot-dns-corenetworks

[![Build Status](https://img.shields.io/drone/build/xoxys/certbot-dns-corenetworks?logo=drone)](https://cloud.drone.io/xoxys/certbot-dns-corenetworks)
[![Python Version](https://img.shields.io/pypi/pyversions/certbot-dns-corenetworks.svg)](https://pypi.org/project/certbot-dns-corenetworks/)
[![PyPi Status](https://img.shields.io/pypi/status/certbot-dns-corenetworks.svg)](https://pypi.org/project/certbot-dns-corenetworks/)
[![PyPi Release](https://img.shields.io/pypi/v/certbot-dns-corenetworks.svg)](https://pypi.org/project/certbot-dns-corenetworks/)
[![Codecov](https://img.shields.io/codecov/c/github/xoxys/certbot-dns-corenetworks)](https://codecov.io/gh/xoxys/certbot-dns-corenetworks)
[![License: MIT](https://img.shields.io/github/license/xoxys/certbot-dns-corenetworks)](LICENSE)

## Install

Install this package via pip in the same python environment where you installed your certbot.

```console
pip install certbot-dns-corenetworks
```

## Usage

To start using DNS authentication for the Core Networks DNS API, pass the following arguments on certbot's command line:

| Option                                                               | Description                                      |
|----------------------------------------------------------------------|--------------------------------------------------|
| `--authenticator certbot-dns-corenetworks:dns-corenetworks`          | select the authenticator plugin (Required)       |
| `--certbot-dns-corenetworks:dns-corenetworks-credentials`            | Hetzner DNS API credentials INI file. (Required) |
| `--certbot-dns-corenetworks:dns-corenetworks-propagation-seconds`    | Seconds to wait for the TXT record to propagate  |

## Credentials

```ini
certbot_dns_corenetworks:dns_corenetworks_username = asaHB12r
certbot_dns_corenetworks:dns_corenetworks_password = secure_passwor
```

## Examples

To acquire a certificate for `example.com`

```bash
certbot certonly \\
 --authenticator certbot-dns-corenetworks:dns-corenetworks \\
 --certbot-dns-corenetworks:dns-corenetworks-credentials /path/to/my/credentials.ini \\
 -d example.com
```

To acquire a certificate for ``*.example.com``

```bash
certbot certonly \\
    --authenticator certbot-dns-corenetworks:dns-corenetworks \\
    --certbot-dns-corenetworks:dns-corenetworks-credentials /path/to/my/credentials.ini \\
    -d '*.example.com'
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Maintainers and Contributors

[Robert Kaussow](https://github.com/xoxys)
