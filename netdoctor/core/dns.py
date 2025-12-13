"""
DNS wrapper module.

DNS queries using dnspython for record lookups.
"""

import dns.resolver
import dns.exception
from typing import Dict, List, Any, Optional


def query_records(domain: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Query DNS records for a domain.

    Args:
        domain: Domain name to query (e.g., "example.com")

    Returns:
        Dictionary with record types as keys and lists of record dictionaries as values.
        Each record dict contains: type, name, value, ttl (if available)
        Keys: 'A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME'
    """
    results = {
        "A": [],
        "AAAA": [],
        "MX": [],
        "NS": [],
        "TXT": [],
        "CNAME": [],
    }

    # Query A records (IPv4)
    try:
        answers = dns.resolver.resolve(domain, "A")
        for answer in answers:
            results["A"].append(
                {
                    "type": "A",
                    "name": domain,
                    "value": str(answer),
                    "ttl": answer.ttl if hasattr(answer, "ttl") else None,
                }
            )
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.DNSException):
        pass

    # Query AAAA records (IPv6)
    try:
        answers = dns.resolver.resolve(domain, "AAAA")
        for answer in answers:
            results["AAAA"].append(
                {
                    "type": "AAAA",
                    "name": domain,
                    "value": str(answer),
                    "ttl": answer.ttl if hasattr(answer, "ttl") else None,
                }
            )
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.DNSException):
        pass

    # Query MX records (Mail Exchange)
    try:
        answers = dns.resolver.resolve(domain, "MX")
        for answer in answers:
            results["MX"].append(
                {
                    "type": "MX",
                    "name": domain,
                    "value": str(answer.exchange),
                    "priority": answer.preference,
                    "ttl": answer.ttl if hasattr(answer, "ttl") else None,
                }
            )
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.DNSException):
        pass

    # Query NS records (Name Server)
    try:
        answers = dns.resolver.resolve(domain, "NS")
        for answer in answers:
            results["NS"].append(
                {
                    "type": "NS",
                    "name": domain,
                    "value": str(answer),
                    "ttl": answer.ttl if hasattr(answer, "ttl") else None,
                }
            )
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.DNSException):
        pass

    # Query TXT records
    try:
        answers = dns.resolver.resolve(domain, "TXT")
        for answer in answers:
            # TXT records can have multiple strings, join them
            txt_value = "".join([s.decode("utf-8") if isinstance(s, bytes) else s for s in answer.strings])
            results["TXT"].append(
                {
                    "type": "TXT",
                    "name": domain,
                    "value": txt_value,
                    "ttl": answer.ttl if hasattr(answer, "ttl") else None,
                }
            )
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.DNSException):
        pass

    # Query CNAME records
    try:
        answers = dns.resolver.resolve(domain, "CNAME")
        for answer in answers:
            results["CNAME"].append(
                {
                    "type": "CNAME",
                    "name": domain,
                    "value": str(answer),
                    "ttl": answer.ttl if hasattr(answer, "ttl") else None,
                }
            )
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.DNSException):
        pass

    return results
