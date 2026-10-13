"""Tests for the ``Self`` cross-references of the documentation configuration.

The API reference shows ``Self`` in signatures and return types.
Sphinx cannot resolve that name by itself, so docs/conf.py links it to the
class that is being documented.
See https://github.com/collective/icalendar/issues/1790
"""

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

HERE = Path(__file__).parent
REPOSITORY_ROOT = HERE.parent.parent.parent
CONF_PATH = REPOSITORY_ROOT / "docs" / "conf.py"


@pytest.fixture(scope="module")
def docs_conf():
    """Load docs/conf.py the way Sphinx loads it."""
    if not CONF_PATH.is_file():
        pytest.skip("docs/conf.py is not available")
    spec = importlib.util.spec_from_file_location("icalendar_docs_conf", CONF_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeText(str):
    """Stand-in for a docutils text node."""

    __slots__ = ()


class FakeContnode:
    """Stand-in for the content node of a pending cross-reference."""

    def __init__(self, text="Self"):
        self.children = [FakeText(text)]

    def deepcopy(self):
        return FakeContnode(self.children[0])


class FakeDomain:
    """Stand-in for the Python domain of Sphinx."""

    def __init__(self, objects):
        self.objects = objects
        self.resolved = []
        self.labels = []

    def resolve_xref(self, env, fromdocname, builder, ref_type, target, node, contnode):
        self.resolved.append((ref_type, target, fromdocname))
        self.labels.append(contnode.children[0])
        return f"reference to {target} labeled {contnode.children[0]}"


class FakeEnv:
    """Stand-in for the Sphinx build environment."""

    def __init__(self, domain):
        self.domain = domain

    def get_domain(self, name):
        assert name == "py"
        return self.domain


def make_node(**values):
    """Return cross-reference attributes as Sphinx stores them."""
    return {
        "reftarget": "typing.Self",
        "reftype": "class",
        "refdoc": "reference/api/icalendar.prop.boolean",
        **values,
    }


def test_self_reference_candidates_joins_module_and_class(docs_conf):
    """The documented class name is completed with the module name."""
    assert docs_conf.self_reference_candidates(
        "icalendar.prop.boolean", "vBoolean"
    ) == [
        "icalendar.prop.boolean.vBoolean",
        "vBoolean",
    ]


def test_self_reference_candidates_accepts_full_class_name(docs_conf):
    """A class name that is already complete is used as it is."""
    assert docs_conf.self_reference_candidates(
        "icalendar.prop.boolean", "icalendar.prop.boolean.vBoolean"
    ) == ["icalendar.prop.boolean.vBoolean"]


def test_self_reference_candidates_requires_class_context(docs_conf):
    """Without a class context, there is nothing to link to."""
    assert docs_conf.self_reference_candidates("icalendar.prop.boolean", None) == []


def test_resolve_self_reference_links_to_the_documented_class(docs_conf):
    """``Self`` becomes a link to the class that is being documented."""
    domain = FakeDomain({"icalendar.prop.boolean.vBoolean": object()})
    env = FakeEnv(domain)
    app = SimpleNamespace(builder=object())
    node = make_node(**{"py:module": "icalendar.prop.boolean", "py:class": "vBoolean"})
    result = docs_conf.resolve_self_reference(app, env, node, FakeContnode())
    assert result == "reference to icalendar.prop.boolean.vBoolean labeled vBoolean"
    assert domain.resolved == [
        (
            "class",
            "icalendar.prop.boolean.vBoolean",
            "reference/api/icalendar.prop.boolean",
        )
    ]


def test_resolve_self_reference_shows_the_short_class_name(docs_conf):
    """The link shows the name of the class without the module name."""
    domain = FakeDomain({"icalendar.prop.boolean.vBoolean": object()})
    env = FakeEnv(domain)
    app = SimpleNamespace(builder=object())
    node = make_node(**{"py:module": "icalendar.prop.boolean", "py:class": "vBoolean"})
    docs_conf.resolve_self_reference(app, env, node, FakeContnode())
    assert domain.labels == ["vBoolean"]


def test_resolve_self_reference_ignores_other_types(docs_conf):
    """Other type references are left alone."""
    domain = FakeDomain({})
    env = FakeEnv(domain)
    app = SimpleNamespace(builder=object())
    node = make_node(reftarget="list")
    assert docs_conf.resolve_self_reference(app, env, node, FakeContnode()) is None
    assert domain.resolved == []


def test_resolve_self_reference_requires_a_known_class(docs_conf):
    """References without a class or with an unknown class are left alone."""
    domain = FakeDomain({})
    env = FakeEnv(domain)
    app = SimpleNamespace(builder=object())
    without_class = make_node(**{"py:module": "icalendar.prop.boolean"})
    unknown_class = make_node(
        **{"py:module": "icalendar.prop.boolean", "py:class": "vBoolean"}
    )
    assert (
        docs_conf.resolve_self_reference(app, env, without_class, FakeContnode())
        is None
    )
    assert (
        docs_conf.resolve_self_reference(app, env, unknown_class, FakeContnode())
        is None
    )
    assert domain.resolved == []


def test_setup_connects_the_missing_reference_handler(docs_conf):
    """The handler is registered for missing cross-references."""
    connected = []
    app = SimpleNamespace(
        connect=lambda *args, **kwargs: connected.append((args, kwargs))
    )
    assert docs_conf.setup(app) == {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
    assert connected == [
        (("missing-reference", docs_conf.resolve_self_reference), {"priority": 450})
    ]
