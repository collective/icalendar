"""Regenerate the docstring-quality baseline used by ``test_docstrings.py``.

Run this script after fixing a docstring, so its checks are no longer
listed as known violations, or after confirming that a newly reported
violation is a real, pre-existing issue you don't intend to fix in the
current change.

.. code-block:: shell

    python src/icalendar/tests/generate_docstring_baseline.py
"""

from __future__ import annotations

import json

from icalendar.tests.test_docstrings import BASELINE_PATH, CHECKS, DOCUMENTED_OBJECTS


def main() -> None:
    baseline = {}
    for check_name, check in CHECKS.items():
        violations = []
        for documented in DOCUMENTED_OBJECTS:
            result = check(documented)
            if result.applicable and not result.ok:
                violations.append(documented.qualname)
        baseline[check_name] = sorted(violations)

    BASELINE_PATH.write_text(
        json.dumps(baseline, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    total = sum(len(v) for v in baseline.values())
    print(
        f"Wrote {total} known violations across {len(baseline)} checks to {BASELINE_PATH}"
    )


if __name__ == "__main__":
    main()
