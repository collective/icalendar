import base64

from icalendar import vBinary


def test_vBinary_binary_preservation():
    """Verify that vBinary preserves non-UTF-8 binary data correctly.
    This tests for the data corruption issue where binary data was incorrectly
    treated as UTF-8.
    """
    # JPEG start sequence - NOT valid UTF-8
    binary_data = b"\xff\xd8\xff\xe0"

    # Initialize vBinary with raw bytes
    prop = vBinary(binary_data)

    # Check that to_ical() returns the correct Base64 of the original bytes
    expected_b64 = base64.b64encode(binary_data)
    assert prop.to_ical() == expected_b64

    # Check that ical_value returns the original bytes
    assert prop.ical_value == binary_data


def test_vBinary_roundtrip_with_corruption_candidate():
    """Test a round-trip with data that previously caused corruption."""
    # Binary data that is often mangled by UTF-8 'replace'
    mangled_data = b"binary \x80\x81\x82 data"

    prop = vBinary(mangled_data)
    ical = prop.to_ical()

    # Decoded value should match original
    decoded = vBinary.from_ical(ical)
    assert decoded == mangled_data
