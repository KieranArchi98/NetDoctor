"""
Unit tests for DNS module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import dns.resolver
import dns.exception

from netdoctor.core.dns import query_records


@patch("dns.resolver.resolve")
def test_query_records_a_record(mock_resolve):
    """Test querying A records."""
    # Mock A record response
    mock_answer = Mock()
    mock_answer.__str__ = Mock(return_value="192.0.2.1")
    mock_answer.ttl = 300

    def resolve_side_effect(domain, record_type):
        if record_type == "A":
            return [mock_answer]
        raise dns.resolver.NoAnswer()

    mock_resolve.side_effect = resolve_side_effect

    results = query_records("example.com")

    assert "A" in results
    assert len(results["A"]) == 1
    assert results["A"][0]["type"] == "A"
    assert results["A"][0]["value"] == "192.0.2.1"
    assert results["A"][0]["ttl"] == 300


@patch("dns.resolver.resolve")
def test_query_records_aaaa_record(mock_resolve):
    """Test querying AAAA records."""
    # Mock AAAA record response
    mock_answer = Mock()
    mock_answer.__str__ = Mock(return_value="2001:db8::1")
    mock_answer.ttl = 300

    def resolve_side_effect(domain, record_type):
        if record_type == "AAAA":
            return [mock_answer]
        raise dns.resolver.NoAnswer()

    mock_resolve.side_effect = resolve_side_effect

    results = query_records("example.com")

    assert "AAAA" in results
    assert len(results["AAAA"]) == 1
    assert results["AAAA"][0]["type"] == "AAAA"
    assert results["AAAA"][0]["value"] == "2001:db8::1"


@patch("dns.resolver.resolve")
def test_query_records_mx_record(mock_resolve):
    """Test querying MX records."""
    # Mock MX record response
    mock_answer = Mock()
    mock_answer.exchange = Mock()
    mock_answer.exchange.__str__ = Mock(return_value="mail.example.com")
    mock_answer.preference = 10
    mock_answer.ttl = 300

    def resolve_side_effect(domain, record_type):
        if record_type == "MX":
            return [mock_answer]
        raise dns.resolver.NoAnswer()

    mock_resolve.side_effect = resolve_side_effect

    results = query_records("example.com")

    assert "MX" in results
    assert len(results["MX"]) == 1
    assert results["MX"][0]["type"] == "MX"
    assert results["MX"][0]["value"] == "mail.example.com"
    assert results["MX"][0]["priority"] == 10


@patch("dns.resolver.resolve")
def test_query_records_ns_record(mock_resolve):
    """Test querying NS records."""
    # Mock NS record response
    mock_answer1 = Mock()
    mock_answer1.__str__ = Mock(return_value="ns1.example.com")
    mock_answer1.ttl = 300

    mock_answer2 = Mock()
    mock_answer2.__str__ = Mock(return_value="ns2.example.com")
    mock_answer2.ttl = 300

    def resolve_side_effect(domain, record_type):
        if record_type == "NS":
            return [mock_answer1, mock_answer2]
        raise dns.resolver.NoAnswer()

    mock_resolve.side_effect = resolve_side_effect

    results = query_records("example.com")

    assert "NS" in results
    assert len(results["NS"]) == 2
    assert results["NS"][0]["value"] == "ns1.example.com"
    assert results["NS"][1]["value"] == "ns2.example.com"


@patch("dns.resolver.resolve")
def test_query_records_txt_record(mock_resolve):
    """Test querying TXT records."""
    # Mock TXT record response
    mock_answer = Mock()
    mock_answer.strings = [b"v=spf1", b"include:_spf.example.com"]
    mock_answer.ttl = 300

    def resolve_side_effect(domain, record_type):
        if record_type == "TXT":
            return [mock_answer]
        raise dns.resolver.NoAnswer()

    mock_resolve.side_effect = resolve_side_effect

    results = query_records("example.com")

    assert "TXT" in results
    assert len(results["TXT"]) == 1
    assert results["TXT"][0]["type"] == "TXT"
    assert "spf1" in results["TXT"][0]["value"]


@patch("dns.resolver.resolve")
def test_query_records_cname_record(mock_resolve):
    """Test querying CNAME records."""
    # Mock CNAME record response
    mock_answer = Mock()
    mock_answer.__str__ = Mock(return_value="www.example.com")
    mock_answer.ttl = 300

    def resolve_side_effect(domain, record_type):
        if record_type == "CNAME":
            return [mock_answer]
        raise dns.resolver.NoAnswer()

    mock_resolve.side_effect = resolve_side_effect

    results = query_records("example.com")

    assert "CNAME" in results
    assert len(results["CNAME"]) == 1
    assert results["CNAME"][0]["type"] == "CNAME"
    assert results["CNAME"][0]["value"] == "www.example.com"


@patch("dns.resolver.resolve")
def test_query_records_multiple_record_types(mock_resolve):
    """Test querying multiple record types."""
    mock_a = Mock()
    mock_a.__str__ = Mock(return_value="192.0.2.1")
    mock_a.ttl = 300

    mock_mx = Mock()
    mock_mx.exchange = Mock()
    mock_mx.exchange.__str__ = Mock(return_value="mail.example.com")
    mock_mx.preference = 10
    mock_mx.ttl = 300

    def resolve_side_effect(domain, record_type):
        if record_type == "A":
            return [mock_a]
        elif record_type == "MX":
            return [mock_mx]
        raise dns.resolver.NoAnswer()

    mock_resolve.side_effect = resolve_side_effect

    results = query_records("example.com")

    assert len(results["A"]) == 1
    assert len(results["MX"]) == 1
    assert len(results["AAAA"]) == 0
    assert len(results["NS"]) == 0
    assert len(results["TXT"]) == 0
    assert len(results["CNAME"]) == 0


@patch("dns.resolver.resolve")
def test_query_records_no_answer(mock_resolve):
    """Test handling when no records are found."""
    mock_resolve.side_effect = dns.resolver.NoAnswer()

    results = query_records("nonexistent.example.com")

    # All record types should be empty lists
    assert len(results["A"]) == 0
    assert len(results["AAAA"]) == 0
    assert len(results["MX"]) == 0
    assert len(results["NS"]) == 0
    assert len(results["TXT"]) == 0
    assert len(results["CNAME"]) == 0


@patch("dns.resolver.resolve")
def test_query_records_nxdomain(mock_resolve):
    """Test handling NXDOMAIN (domain doesn't exist)."""
    mock_resolve.side_effect = dns.resolver.NXDOMAIN()

    results = query_records("nonexistent.example.com")

    # All record types should be empty lists
    assert len(results["A"]) == 0
    assert len(results["AAAA"]) == 0


@patch("dns.resolver.resolve")
def test_query_records_dns_exception(mock_resolve):
    """Test handling DNS exceptions."""
    mock_resolve.side_effect = dns.exception.DNSException("DNS error")

    results = query_records("example.com")

    # Should return empty results without crashing
    assert isinstance(results, dict)
    assert "A" in results
    assert len(results["A"]) == 0


@patch("dns.resolver.resolve")
def test_query_records_all_types_structure(mock_resolve):
    """Test that all record types are present in results."""
    mock_resolve.side_effect = dns.resolver.NoAnswer()

    results = query_records("example.com")

    # Verify all expected record types are present
    expected_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]
    for record_type in expected_types:
        assert record_type in results
        assert isinstance(results[record_type], list)

