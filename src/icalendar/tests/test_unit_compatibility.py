import pytest

from icalendar.compatibility import deprecate_for_version_8


def test_deprecate_for_version_8_issues_warning():
    def _my_func():
        return 42

    wrapped = deprecate_for_version_8(_my_func)
    with pytest.warns(DeprecationWarning, match="my_func is deprecated and will be removed in icalendar 8"):
        result = wrapped()
    assert result == 42


def test_deprecate_for_version_8_public_name():
    def _my_func():
        pass

    wrapped = deprecate_for_version_8(_my_func)
    with pytest.warns(DeprecationWarning):
        wrapped()
    assert wrapped.__name__ == "my_func"


def test_deprecate_for_version_8_passes_args():
    def _add(a, b=0):
        return a + b

    wrapped = deprecate_for_version_8(_add)
    with pytest.warns(DeprecationWarning):
        result = wrapped(3, b=4)
    assert result == 7


def test_deprecate_for_version_8_no_leading_underscore():
    def my_func():
        return "ok"

    wrapped = deprecate_for_version_8(my_func)
    with pytest.warns(DeprecationWarning, match="my_func is deprecated"):
        result = wrapped()
    assert result == "ok"
    assert wrapped.__name__ == "my_func"
