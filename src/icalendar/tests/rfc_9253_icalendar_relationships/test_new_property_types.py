"""Test the new property types UID and XML-REFERENCE.

- creation
- parameters
- serialization
- deserialization
- attributes
"""

import pytest

from icalendar import vUid, vUri, vXmlReference


@pytest.fixture(
    params=[
        "123e4567-e89b-12d3-a456-426614174000",
        "550e8400-e29b-41d4-a716-446655440000",
    ]
)
def uid(request):
    return request.param


@pytest.fixture(
    params=[
        "https://example.com/events",
        "https://example.com/tasks/01234567-abcd1234.ics",
    ]
)
def uri(request):
    return request.param


@pytest.fixture(
    params=[
        (
            "https://example.com/xmlDocs/bidFramework.xml#xpointer(descendant::CostStruc/range-to(following::CostStrucEND[1]))",
            "descendant::CostStruc/range-to(following::CostStrucEND[1])",
        ),
        (
            "https://www.w3.org/TR/2003/REC-xptr-framework-20030325/#xpointer(id('r%C3%A9sum%C3%A9'))",
            "id('résumé')",
        ),
    ]
)
def xml_reference(request):
    return request.param


def test_uid_creation(uid):
    """Test creation of UID property."""
    uid_prop = vUid(uid)
    assert repr(uid_prop) == f"vUid({uid!r})"
    assert uid_prop.ics_value == uid
    assert uid_prop.uid == uid
    assert_default_parameters(uid_prop)


def test_uid_new(test_uid):
    """The new uid should be tested."""
    uid_prop = vUid.new()
    assert uid_prop.uid == test_uid
    assert_default_parameters(uid_prop)
    assert uid_prop.params.value == "UID"


def test_vUri_creation(uri):
    """Test creation of a URI property."""
    uri_prop = vUri(uri)
    assert str(uri_prop) == uri
    assert uri_prop.ics_value == uri
    assert uri_prop.uri == uri
    assert_default_parameters(uri_prop)
    assert uri_prop.params.value in ("URI", None)


def test_vXmlReference_creation(xml_reference):
    """Test creation of a URI property."""
    uri, x_pointer = xml_reference
    xml_prop = vXmlReference(uri)
    assert str(xml_prop) == uri
    assert xml_prop.ics_value == uri
    assert xml_prop.uri == uri
    assert_default_parameters(xml_prop)
    assert xml_prop.x_pointer == x_pointer
    assert xml_prop.params.value == "XML-REFERENCE"


def assert_default_parameters(prop):
    """Test an empty property."""
    assert prop.LABEL is None
    assert prop.LANGUAGE is None
    assert prop.FMTTYPE is None
    assert prop.LINKREL is None
    assert repr(prop).startswith(prop.__class__.__name__ + "(")
    assert repr(prop).endswith(")")
    assert prop.VALUE == prop.params.value == prop.params.get("VALUE")


@pytest.mark.parametrize("no_x_pointer", ["", "asd)", "xpointer(id('r%C3%A9sum%C3%A9'"])
def test_not_x_pointer(no_x_pointer):
    """Test that the x_pointer throws a value error."""
    xml = vXmlReference("http://asd#" + no_x_pointer)
    with pytest.raises(ValueError):
        xml.x_pointer  # noqa: B018


mark_valid_values = pytest.mark.parametrize(
    ("name", "value"),
    [
        ("LABEL", None),
        ("LABEL", "Venue"),
        ("LANGUAGE", None),
        ("LANGUAGE", "de"),
        ("LANGUAGE", "en-gb"),
        ("LINKREL", None),
        ("LINKREL", "SOURCE"),
        ("LINKREL", "https://example.com/linkrel/derivedFrom"),
        ("LINKREL", "icon"),
        ("FMTTYPE", None),
        ("FMTTYPE", "text/html"),
    ],
)


def vUri_example():
    """New example instance."""
    return vUri("http://example.com")


def vXmlReference_example():
    """New example instance."""
    return vXmlReference("http://example.com")


mark_new_prop = pytest.mark.parametrize(
    "new_prop", [vUri_example, vUid.new, vXmlReference_example]
)


@mark_new_prop
@mark_valid_values
def test_set_attributes(new_prop, name, value):
    """Set the values and test"""
    prop = new_prop()
    assert hasattr(prop, name)
    setattr(prop, name, value)
    print(prop.params)
    assert getattr(prop, name) == value
    if value is None:
        assert name not in prop.params
    else:
        assert prop.params[name] == value


@mark_new_prop
@mark_valid_values
def test_delete_attribute_setting_to_none(new_prop, name, value):
    """The attribute can be deleted by setting to None."""
    prop = new_prop()
    setattr(prop, name, value)
    setattr(prop, name, None)
    assert name not in prop.params
    assert getattr(prop, name) is None


@mark_new_prop
@mark_valid_values
def test_delete_attribute(new_prop, name, value):
    """The attribute can be deleted."""
    prop = new_prop()
    setattr(prop, name, value)
    delattr(prop, name)
    assert name not in prop.params
    assert getattr(prop, name) is None
