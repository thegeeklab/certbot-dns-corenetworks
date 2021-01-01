# certbot-dns-corenetworks

[![Build Status](https://img.shields.io/drone/build/thegeeklab/certbot-dns-corenetworks?logo=drone)](https://cloud.drone.io/thegeeklab/certbot-dns-corenetworks)
[![Python Version](https://img.shields.io/pypi/pyversions/certbot-dns-corenetworks.svg)](https://pypi.org/project/certbot-dns-corenetworks/)
[![PyPi Status](https://img.shields.io/pypi/status/certbot-dns-corenetworks.svg)](https://pypi.org/project/certbot-dns-corenetworks/)
[![PyPi Release](https://img.shields.io/pypi/v/certbot-dns-corenetworks.svg)](https://pypi.org/project/certbot-dns-corenetworks/)
[![Codecov](https://img.shields.io/codecov/c/github/thegeeklab/certbot-dns-corenetworks)](https://codecov.io/gh/thegeeklab/certbot-dns-corenetworks)
[![GitHub contributors](https://img.shields.io/github/contributors/thegeeklab/certbot-dns-corenetworks)](https://github.com/thegeeklab/certbot-dns-corenetworks/graphs/contributors)
[![License: MIT](https://img.shields.io/github/license/thegeeklab/certbot-dns-corenetworks)](https://github.com/thegeeklab/certbot-dns-corenetworks/blob/main/LICENSE)

## Install

Install this package via pip in the same python environment where you installed your certbot.

```console
pip install certbot-dns-corenetworks
```

## Usage

To start using DNS authentication for the Core Networks DNS API, pass the following arguments on certbot's command line:

| Option                                                            | Description                                      |
| ----------------------------------------------------------------- | ------------------------------------------------ |
| `--authenticator dns-corenetworks`       | select the authenticator plugin (Required)       |
| `--dns-corenetworks-credentials`         | Hetzner DNS API credentials INI file. (Required) |
| `--dns-corenetworks-propagation-seconds` | Seconds to wait for the TXT record to propagate  |

## Credentials

```ini
dns_corenetworks_username = asaHB12r
dns_corenetworks_password = secure_passwor
```

## Examples

To acquire a certificate for `example.com`

```bash
certbot certonly \
 --authenticator dns-corenetworks \
 --dns-corenetworks-credentials /path/to/my/credentials.ini \
 -d example.com
```

To acquire a certificate for `*.example.com`

```bash
certbot certonly \
    --authenticator dns-corenetworks \
    --dns-corenetworks-credentials /path/to/my/credentials.ini \
    -d '*.example.com'
```

## Contributors

Special thanks goes to all [contributors](https://github.com/thegeeklab/certbot-dns-corenetworks/graphs/contributors). If you would like to contribute,
please see the [instructions](https://github.com/thegeeklab/certbot-dns-corenetworks/blob/main/CONTRIBUTING.md).

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/thegeeklab/certbot-dns-corenetworks/blob/main/LICENSE) file for details.
