Added automated tests, in :file:`src/icalendar/tests/test_docstrings.py`, that check docstrings across the package against the documentation style guide: recognized section headings, and required ``Parameters``, ``Returns``, ``Raises``, and ``Examples`` sections where a signature or function body calls for them.
Pre-existing violations are tracked in a baseline file, :file:`src/icalendar/tests/docstring_known_violations.json`, so the backlog can be fixed incrementally without failing the whole suite; new violations aren't allowed.
I used AI (Claude Code) to help design and implement these checks.
@gagana2023
