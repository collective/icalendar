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
    assert_equals(
        vCalAddress("mailto:user@example.com"), vCalAddress("user@example.com")
    )
    assert_equals(
        vCalAddress("MAILTO:user@example.com"), vCalAddress("user@example.com")
    )
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


def test_equality_against_plain_str_coerces_to_vcaladdress():
    """A plain str is converted to vCalAddress before comparing.

    This is the use case the maintainer asked for in the review of
    #1901: ``my_email in event.attendees`` must work when attendees
    are vCalAddress objects and my_email is a plain string.
    """
    assert vCalAddress("mailto:a@example.com") == "a@example.com"
    assert vCalAddress("mailto:a@example.com") == "mailto:A@EXAMPLE.com"
    assert "a@example.com" == vCalAddress("mailto:a@example.com")  # reflected
    assert vCalAddress("mailto:a@example.com") != "b@example.com"


def test_str_that_cannot_be_an_address_is_not_equal():
    """A str that fails vCalAddress() construction is never equal.

    vCalAddress.__new__ rejects CR and LF; per the review of #1901,
    such strings make __eq__ return NotImplemented, so the comparison
    is False in both directions instead of raising.
    """
    assert vCalAddress("mailto:a@example.com") != "a\nb@example.com"
    assert "a\nb@example.com" != vCalAddress("mailto:a@example.com")


def test_ne_is_consistent_with_eq():
    """``!=`` must be the exact negation of ``==``.

    vCalAddress extends str, so without an explicit __ne__, ``!=``
    would use str.__ne__ (plain string comparison) and disagree with
    __eq__: case-insensitively equal addresses would be both ``==``
    and ``!=``. Found via the coverage review in #1901.

    Results are bound to names first so the comparison operators are
    genuinely exercised (and the linter does not rewrite the check).
    """
    a = vCalAddress("mailto:a@example.com")
    eq_forward = a == "MAILTO:A@EXAMPLE.COM"
    ne_forward = a != "MAILTO:A@EXAMPLE.COM"
    eq_reflected = "MAILTO:A@EXAMPLE.COM" == a
    ne_reflected = "MAILTO:A@EXAMPLE.COM" != a
    assert eq_forward
    assert eq_reflected
    assert ne_forward == (not eq_forward)
    assert ne_reflected == (not eq_reflected)

    eq_other = a == "b@example.com"
    ne_other = a != "b@example.com"
    assert not eq_other
    assert ne_other == (not eq_other)


def test_comparison_against_other_types_is_not_equal():
    """Comparison against non-str types falls back to NotImplemented."""
    a = vCalAddress("mailto:a@example.com")
    eq_int = a == 123
    ne_int = a != 123
    assert not eq_int
    assert ne_int
    eq_list = a == ["mailto:a@example.com"]
    ne_list = a != ["mailto:a@example.com"]
    assert not eq_list
    assert ne_list


def test_mixed_str_comparison_hash_limitation_is_documented():
    """Known limitation, also documented in vCalAddress.__eq__.

    Hash consistency is guaranteed only between two vCalAddress
    instances: a plain str hashes by its literal value, which cannot
    be changed. The maintainer accepted this in the review of #1901.
    """
    a = vCalAddress("mailto:a@example.com")
    b = "MAILTO:A@EXAMPLE.COM"
    assert a == b
    assert b == a
    assert hash(a) != hash(b)  # accepted limitation — see docstring


def test_equal_addresses_deduplicate_in_sets():
    """Equal addresses collapse in sets and dict keys."""
    addresses = {
        vCalAddress("mailto:User@Example.com"),
        vCalAddress("MAILTO:user@example.com"),
        vCalAddress("user@example.com"),
    }
    assert len(addresses) == 1
    assert vCalAddress("USER@EXAMPLE.COM") in addresses


def test_equality_ignores_parameters():
    """Equality depends only on the email address, not on .params.

    Suggested by DhyeyBuch in the review of #1901: two addresses with
    the same email but different parameters (e.g. CN) still compare
    equal. Passes against the current __eq__, which compares only the
    lowercased email — no implementation change needed.
    """
    a = vCalAddress("mailto:user@example.com")
    a.params["CN"] = "Alice"
    b = vCalAddress("mailto:user@example.com")
    b.params["CN"] = "Bob"
    assert_equals(a, b)
