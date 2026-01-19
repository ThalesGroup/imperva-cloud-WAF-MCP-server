import pytest

from cwaf_external_mcp.utilities.parameters_parser import _coerce_list


def test_none_returns_none():
    assert _coerce_list(None, int) is None


def test_iterable_of_ints():
    assert _coerce_list([1, 2, 3], int) == [1, 2, 3]


def test_iterable_with_none_and_empty():
    assert _coerce_list([None, "", "  ", 4], int) == [4]


def test_string_json_array():
    assert _coerce_list("[1,2,3]", int) == [1, 2, 3]


def test_string_double_encoded_json():
    assert _coerce_list('"[1,2,3]"', int) == [1, 2, 3]


def test_string_csv():
    assert _coerce_list("1,2,3", int) == [1, 2, 3]


def test_string_bracketed_csv():
    assert _coerce_list(" [ 1 , 2 ] ", int) == [1, 2]


def test_string_with_backticks():
    assert _coerce_list("`1,2,3`", int) == [1, 2, 3]


def test_string_with_whitespace():
    assert _coerce_list("  4 5 6  ", int) == [4, 5, 6]


def test_string_empty():
    assert _coerce_list("", int) is None


def test_strings_list():
    assert _coerce_list('["a", "b", "c"]', str) == ["a", "b", "c"]


def test_strings_list_with_escaping():
    assert _coerce_list('["a", "b", "c"]', str) == ["a", "b", "c"]


def test_strings_list_with_escaping2():
    assert _coerce_list('["a", "b", "c"]', str) == ["a", "b", "c"]


def test_strings_list_with_escaping3():
    assert _coerce_list('["ACL"]', str) == ["ACL"]


def test_string_non_list_json():
    assert _coerce_list('"notalist"', str) == ["notalist"]


def test_type_error():
    with pytest.raises(TypeError):
        _coerce_list(123.45, int)
