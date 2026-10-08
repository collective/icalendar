from icalendar.parser import Parameters
from icalendar.prop import vCalAddress

txt = b"MAILTO:maxm@mxm.dk"
a = vCalAddress(txt)
a.params["cn"] = "Max M"


def test_to_ical():
    assert a.to_ical() == txt


def test_params():
    assert isinstance(a.params, Parameters)
    assert a.params == {"CN": "Max M"}


def test_from_ical():
    assert vCalAddress.from_ical(txt) == "MAILTO:maxm@mxm.dk"


def test_repr():
    instance = vCalAddress("value")
    assert repr(instance) == "vCalAddress('value')"


def test_email_malformed():
    """Sometimes, people forget to add mailto that."""
    address = vCalAddress("me@you.we")
    assert address.email == "me@you.we"


def test_email_mailto():
    """Email with a normal mailto link."""
    address = vCalAddress("mailto:icalendar@email.list")
    assert address.email == "icalendar@email.list"


def test_capital_email():
    """mailto can be capital letters."""
    address = vCalAddress("MAILTO:yemaya@posteo.net")
    assert address.email == "yemaya@posteo.net"


def test_name():
    """We want the name, too!"""
    address = vCalAddress("MAILTO:yemaya@posteo.net")
    assert address.name == ""
    address.params["CN"] = "name!"
    assert address.name == "name!"


def test_set_the_name():
    address = vCalAddress("MAILTO:yemaya@posteo.net")
    address.name = "Yemaya :)"
    assert address.name == "Yemaya :)"
    assert address.params["CN"] == "Yemaya :)"


def assert_equals(a, b):
    """Check a == b, b == a and that both hash the same."""
    assert a == b
    assert b == a
    assert hash(a) == hash(b)


def assert_not_equals(a, b):
    """Check a != b and b != a."""
    assert a != b
    assert b != a


def test_equality_ignores_email_case():
    """Email addresses are case-insensitive. See issue #1896."""
    assert_equals(
        vCalAddress("mailto:User@Example.COM"),
        vCalAddress("mailto:user@example.com"),
    )


def test_equality_mailto_prefix_is_optional():
    """mailto: may be present on either, both or neither side."""
    assert_equals(vCalAddress("mailto:user@example.com"), vCalAddress("user@example.com"))
    assert_equals(vCalAddress("MAILTO:user@example.com"), vCalAddress("user@example.com"))
    assert_equals(vCalAddress("user@example.com"), vCalAddress("user@example.com"))


def test_inequality_for_different_emails():
    assert_not_equals(
        vCalAddress("mailto:alice@example.com"),
        vCalAddress("mailto:bob@example.com"),
    )
    assert_not_equals(
        vCalAddress("mailto:alice@example.com"),
        vCalAddress("alice@example.org"),
    )


def test_equality_against_plain_str_keeps_str_semantics():
    """Comparing with a plain str falls back to exact str comparison.

    This is intentional: normalizing here too would break the
    hash invariant, as a plain str hashes by its literal value.
    """
    assert vCalAddress("mailto:a@example.com") == "mailto:a@example.com"
    assert vCalAddress("mailto:a@example.com") != "mailto:A@example.com"


def test_mixed_str_comparison_hash_limitation_is_documented():
    """Known limitation, also documented in vCalAddress.__eq__.

    Comparison with a plain str keeps the exact str semantics it always
    had (see test_from_ical), so the pair below compares equal while
    their hashes differ. Hash consistency is guaranteed only between
    two vCalAddress instances.

    This cannot be "fixed": returning False for str would break backward
    compatibility, and normalizing the str side as well would only create
    more equal-but-differently-hashed pairs (a plain str hashes by its
    literal value and that cannot be changed).
    """
    a = vCalAddress("mailto:a@example.com")
    b = "mailto:a@example.com"
    assert a == b  # exact str semantics, unchanged legacy behavior
    assert b == a
    assert hash(a) != hash(b)  # known, documented limitation — see docstring


def test_equal_addresses_deduplicate_in_sets():
    """Equal addresses collapse in sets and dict keys."""
    addresses = {
        vCalAddress("mailto:User@Example.com"),
        vCalAddress("MAILTO:user@example.com"),
        vCalAddress("user@example.com"),
    }
    assert len(addresses) == 1
    assert vCalAddress("USER@EXAMPLE.COM") in addresses
