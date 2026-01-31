# Copyright Thales 2026
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from cwaf_external_mcp.utilities.parameters_parser import (
    _coerce_list,
    _to_int,
    _to_bool,
    _to_str,
)


class TestToInt:
    """Tests for _to_int function."""

    def test_to_int_with_none(self):
        """Test _to_int with None returns None."""
        assert _to_int(None) is None

    def test_to_int_with_empty_string(self):
        """Test _to_int with empty string returns None."""
        assert _to_int("") is None
        assert _to_int("   ") is None

    def test_to_int_with_integer_string(self):
        """Test _to_int converts string to int."""
        assert _to_int("123") == 123
        assert _to_int("  456  ") == 456

    def test_to_int_with_integer(self):
        """Test _to_int with integer returns integer."""
        assert _to_int(789) == 789


class TestToBool:
    """Tests for _to_bool function."""

    def test_to_bool_with_none(self):
        """Test _to_bool with None returns None."""
        assert _to_bool(None) is None

    def test_to_bool_with_bool(self):
        """Test _to_bool with boolean returns boolean."""
        assert _to_bool(True) is True
        assert _to_bool(False) is False

    def test_to_bool_with_integer(self):
        """Test _to_bool with integers converts to bool."""
        assert _to_bool(1) is True
        assert _to_bool(0) is False
        assert _to_bool(5) is True

    def test_to_bool_with_true_strings(self):
        """Test _to_bool with true-like strings."""
        assert _to_bool("true") is True
        assert _to_bool("TRUE") is True
        assert _to_bool("1") is True
        assert _to_bool("yes") is True
        assert _to_bool("y") is True
        assert _to_bool("on") is True

    def test_to_bool_with_false_strings(self):
        """Test _to_bool with false-like strings."""
        assert _to_bool("false") is False
        assert _to_bool("FALSE") is False
        assert _to_bool("0") is False
        assert _to_bool("no") is False
        assert _to_bool("n") is False
        assert _to_bool("off") is False

    def test_to_bool_with_invalid_string(self):
        """Test _to_bool with invalid string raises ValueError."""
        with pytest.raises(ValueError):
            _to_bool("invalid")


class TestToStr:
    """Tests for _to_str function."""

    def test_to_str_with_none(self):
        """Test _to_str with None returns None."""
        assert _to_str(None) is None

    def test_to_str_with_empty_string(self):
        """Test _to_str with empty string returns None."""
        assert _to_str("") is None
        assert _to_str("   ") is None

    def test_to_str_with_string(self):
        """Test _to_str returns trimmed string."""
        assert _to_str("hello") == "hello"
        assert _to_str("  world  ") == "world"

    def test_to_str_with_backticks(self):
        """Test _to_str strips backticks."""
        assert _to_str("`test`") == "test"


class TestCoerceList:
    """Tests for _coerce_list function."""

    def test_coerce_list_with_none(self):
        """Test _coerce_list with None returns None."""
        assert _coerce_list(None, str) is None

    def test_coerce_list_with_empty_string(self):
        """Test _coerce_list with empty string returns None."""
        assert _coerce_list("", str) is None
        assert _coerce_list("   ", str) is None

    def test_coerce_list_with_list(self):
        """Test _coerce_list with list."""
        assert _coerce_list([1, 2, 3], int) == [1, 2, 3]
        assert _coerce_list(["a", "b", "c"], str) == ["a", "b", "c"]

    def test_coerce_list_with_tuple(self):
        """Test _coerce_list with tuple."""
        assert _coerce_list((1, 2, 3), int) == [1, 2, 3]

    def test_coerce_list_with_set(self):
        """Test _coerce_list with set."""
        result = _coerce_list({1, 2, 3}, int)
        assert len(result) == 3
        assert set(result) == {1, 2, 3}

    def test_coerce_list_skips_none_in_iterable(self):
        """Test _coerce_list skips None values in iterable."""
        assert _coerce_list([1, None, 3], int) == [1, 3]

    def test_coerce_list_skips_empty_strings_in_iterable(self):
        """Test _coerce_list skips empty strings in iterable."""
        assert _coerce_list(["a", "", "c"], str) == ["a", "c"]

    def test_coerce_list_with_json_array_string(self):
        """Test _coerce_list with JSON array string."""
        assert _coerce_list("[1,2,3]", int) == [1, 2, 3]
        assert _coerce_list('["a","b","c"]', str) == ["a", "b", "c"]

    def test_coerce_list_with_double_encoded_json(self):
        """Test _coerce_list with double-encoded JSON."""
        assert _coerce_list('"[1,2,3]"', int) == [1, 2, 3]

    def test_coerce_list_with_csv_string(self):
        """Test _coerce_list with comma-separated values."""
        assert _coerce_list("1,2,3", int) == [1, 2, 3]
        assert _coerce_list("a,b,c", str) == ["a", "b", "c"]

    def test_coerce_list_with_bracketed_csv(self):
        """Test _coerce_list with bracketed CSV."""
        assert _coerce_list("[1, 2, 3]", int) == [1, 2, 3]
        assert _coerce_list("( a , b , c )", str) == ["a", "b", "c"]

    def test_coerce_list_with_backticks(self):
        """Test _coerce_list strips backticks."""
        assert _coerce_list("`1,2,3`", int) == [1, 2, 3]

    def test_coerce_list_with_whitespace_separator(self):
        """Test _coerce_list with whitespace-separated values."""
        assert _coerce_list("1 2 3", int) == [1, 2, 3]

    def test_coerce_list_with_quoted_strings(self):
        """Test _coerce_list handles quoted strings."""
        assert _coerce_list("'a','b','c'", str) == ["a", "b", "c"]
        assert _coerce_list('"a","b","c"', str) == ["a", "b", "c"]

    def test_coerce_list_invalid_type_raises_error(self):
        """Test _coerce_list with invalid type raises TypeError."""
        with pytest.raises(TypeError):
            _coerce_list(123, int)

    def test_coerce_list_empty_parts_returns_none(self):
        """Test _coerce_list with only separators returns None."""
        assert _coerce_list(",,,", str) is None
        assert _coerce_list("   ", str) is None
