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

"""Utilities for parsing parameter values into specific types."""

from __future__ import annotations

import json
import re
from typing import Optional, Union, TypeVar

T = TypeVar("T")


def _coerce_list(value, caster):
    """
    Accepts:
      - None
      - real iterables (list/tuple/set)
      - strings like:
          "[1,2,3]"                  (JSON array)
          "\"[1,2,3]\""              (double-encoded JSON -> supports: "[\"string1\"]")
          "1,2,3" or "  [ 1 , 2 ]  " (CSV/bracketed)
          with or without backticks
    Returns list[T] or None.
    """
    if value is None:
        return None

    # Already an iterable (list/tuple/set)
    if isinstance(value, (list, tuple, set)):
        out = []
        for item in value:
            if item is None:
                continue
            s = str(item).strip().strip("`")
            if s == "":
                continue
            out.append(caster(s))
        return out

    if isinstance(value, str):
        s = value.strip().strip("`")
        if s == "":
            return None

        # Try to peel up to 3 JSON layers (handles "\"[\"string1\"]\"" etc.)
        for _ in range(3):
            try:
                parsed = json.loads(s)
            except json.JSONDecodeError:
                break

            if isinstance(parsed, list):
                # Cast items (stringify first so caster can be uniform)
                return [caster(str(x).strip()) for x in parsed if str(x).strip() != ""]
            if isinstance(parsed, str):
                # Continue peeling if the inner is still a JSON-looking string
                if parsed == s:
                    break
                s = parsed
                continue
            # Non-list, non-string -> stop peeling and fall back
            break

        # Remove simple enclosing [] or ()
        s = re.sub(r"^\s*[\[\(]\s*|\s*[\]\)]\s*$", "", s)

        # Split on commas or whitespace
        parts = [
            p.strip().strip("'").strip('"') for p in re.split(r"[,\s]+", s) if p.strip()
        ]
        if not parts:
            return None
        return [caster(p) for p in parts]

    raise TypeError(f"Expected list/tuple/set or string, got {type(value).__name__}")


def _to_int(v: Union[str, int, None]) -> Optional[int]:
    """Converts the input to an integer or None."""
    if v is None or (isinstance(v, str) and v.strip() == ""):
        return None
    return int(v)


def _to_bool(v: Union[str, bool, int, None]) -> Optional[bool]:
    """Converts the input to a boolean or None."""
    if v is None:
        return None
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    s = str(v).strip().lower()
    if s in {"true", "1", "yes", "y", "on"}:
        return True
    if s in {"false", "0", "no", "n", "off"}:
        return False
    raise ValueError(f"Cannot parse boolean from {v!r}")


def _to_str(v: Union[str, None]) -> Optional[str]:
    """Converts the input to a trimmed string or None."""
    if v is None:
        return None
    s = str(v).strip().strip("`")
    return s if s != "" else None
