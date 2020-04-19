"""DNS Authenticator for Core Networks."""
import logging
import re

import zope.interface  # noqa
from certbot import errors
from certbot import interfaces
from certbot.plugins import dns_common
from corenetworks import CoreNetworks
from corenetworks.exceptions import AuthError
from corenetworks.exceptions import CoreNetworksException

logger = logging.getLogger(__name__)


@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for Core Networks DNS API."""

    description = (
        "Obtain certificates using a DNS TXT record "
        "(if you are using Core Networks for your domains)."
    )
    ttl = 300

    clientCache = {}  # noqa
    nameCache = {}  # noqa

    def __init__(self, *args, **kwargs):
        """Initialize an Core Networks Authenticator."""
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add):  # noqa
        super(Authenticator, cls).add_parser_arguments(add, default_propagation_seconds=60)
        add(
            "credentials",
            help=("Path to Core Networks account credentials INI file"),
            default="/etc/letsencrypt/corenetworks.cfg"
        )

    def more_info(self):  # noqa
        return "This plugin configures a DNS TXT record to respond to a dns-01 challenge using " \
               "the Core Networks DNS API."

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            "credentials", "path to Core Networks API credentials INI file", {
                "username": "Username of the Core Networks API account.",
                "password": "Password of the Core Networks API account.",
            }
        )

    def _follow_cnames(self, domain, validation_name):
        """
        Perform recursive CNAME lookups.

        In case there exist a CNAME for the given validation name a recursive CNAME lookup
        will be performed automatically. If the optional dependency dnspython is not installed,
        the given name is simply returned.
        """
        try:
            import dns.exception  # noqa
            import dns.resolver  # noqa
            import dns.name  # noqa
        except ImportError:
            return validation_name

        resolver = dns.resolver.Resolver()
        name = dns.name.from_text(validation_name)
        while 1:
            try:
                answer = resolver.query(name, "CNAME")
                if 1 <= len(answer):
                    name = answer[0].target
                else:
                    break
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                break
            except (dns.exception.Timeout, dns.resolver.YXDOMAIN, dns.resolver.NoNameservers):
                raise errors.PluginError(
                    "Failed to lookup CNAMEs on your requested domain {0}".format(domain)
                )
        return name.to_text(True)

    def _perform(self, domain, validation_name, validation):
        if validation_name in Authenticator.nameCache:
            resolved = Authenticator.nameCache[validation_name]
        else:
            resolved = self._follow_cnames(domain, validation_name)
            Authenticator.nameCache[validation_name] = resolved

        if resolved != validation_name:
            logger.info("Validation record for %s redirected by CNAME(s) to %s", domain, resolved)

        self._get_corenetworks_client().add_txt_record(domain, resolved, validation, self.ttl)

    def _cleanup(self, domain, validation_name, validation):
        resolved = Authenticator.nameCache[validation_name]
        self._get_corenetworks_client().del_txt_record(domain, resolved, validation)

    def _get_corenetworks_client(self):
        key = self.conf("credentials")

        if key in Authenticator.clientCache:
            client = Authenticator.clientCache[key]
        else:
            client = _CorenetworksClient(
                self.credentials.conf("username"), self.credentials.conf("password")
            )
            Authenticator.clientCache[key] = client

        return client


class _CorenetworksClient(object):
    """Encapsulates all communication with the Core Networks  API."""

    def __init__(self, user, password, auto_commit=True):
        try:
            self.client = CoreNetworks(user, password, auto_commit=auto_commit)
        except AuthError as e:
            raise errors.PluginError("Login failed: {0}".format(str(e)))

    def add_txt_record(self, domain_name, record_name, record_content, record_ttl):
        """
        Add a TXT record using the supplied information.

        Args:
            domain_name (str): The requested domain for validation.
            record_name (str): The record name (typically beginning with "_acme-challenge.").
            record_content (str): The record content (typically the challenge validation).
            record_ttl(int): The record TTL (number of seconds that the record may be cached).

        Raises:
            certbot.errors.PluginError: If an error occurs communicating with the DNS server

        """
        zone = self._find_zone(record_name)
        name = re.sub(r"\.{}$".format(zone), "", record_name)

        try:
            self.client.add_record(
                zone, {
                    "name": name,
                    "type": "TXT",
                    "data": record_content,
                    "ttl": record_ttl
                }
            )
        except CoreNetworksException:
            raise errors.PluginError(
                "Failed to add TXT DNS record {record} to {zone} for {domain}".format(
                    record=record_name, zone=zone, domain=domain_name
                )
            )

    def del_txt_record(self, domain_name, record_name, record_content):
        """
        Delete a TXT record using the supplied information.

        Args:
            domain_name (str): The requested domain for validation.
            record_name (str): The record name (typically beginning with "_acme-challenge.").
            record_content (str): The record content (typically the challenge validation).

        Returns:
            certbot.errors.PluginError: if an error occurs communicating with the DNS server

        """
        zone = self._find_zone(record_name)
        name = re.sub(r"\.{}$".format(zone), "", record_name)

        try:
            info = self.client.records(zone, {"name": name, "type": "TXT", "data": record_content})
            if (len(info) != 1 or info[0]["name"] != name):
                raise NameError("Unknown record")
        except NameError as e:
            raise errors.PluginError(
                "Record {record} not found: {err}".format(record=record_name, err=e)
            )
        except CoreNetworksException as e:
            raise errors.PluginError(
                "Could not lookup record {record}: {err}".format(record=record_name, err=e)
            )

        try:
            self.client.delete_record(zone, {"name": name, "type": "TXT", "data": record_content})
        except CoreNetworksException:
            raise errors.PluginError(
                "Failed to delete TXT DNS record {record} of {zone} for {domain}".format(
                    record=record_name, zone=zone, domain=domain_name
                )
            )

    def _find_zone(self, domain_name):
        """
        Find the base domain name for a given domain name.

        :param str domain_name: The domain name for which to find the corresponding base domain.
        :returns: The base domain name, if found.
        :rtype: str
        :raises certbot.errors.PluginError: if no matching domain is found.
        """
        domain_name_guesses = dns_common.base_domain_name_guesses(domain_name)

        for guess in domain_name_guesses:
            logger.debug("Testing {0} for domain {1}...".format(guess, domain_name))
            try:
                info = self.client.zone(guess)[0]
            except CoreNetworksException:
                continue

            logger.debug("Found zone '{zone}': {info}".format(zone=guess, info=info))
            if not info.get("active"):
                raise errors.PluginError("Zone {0} is not active".format(guess))
            if info.get("type") != "master":
                raise errors.PluginError("Zone {0} is not a master zone".format(guess))

            return guess

        raise errors.PluginError(
            "Unable to determine base domain for {0} using names: {1}".format(
                domain_name, domain_name_guesses
            )
        )
