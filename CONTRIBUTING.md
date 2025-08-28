# Contributing

See our [contributing guidelines](https://icalendar.readthedocs.io/en/latest/contributing.html) for complete information on how to contribute to icalendar.

## Contribution examples

- Reporting issues to the bugtracker.
- Submitting pull requests from a forked icalendar repo.
- Extending the documentation.
- Sponsor a Sprint (https://plone.org/events/sprints/whatis).

## Pull request requirements

> [!IMPORTANT]
> Every pull request must include a change log entry.

Before submitting your pull request, ensure you have met the following requirements.

1. **Add a changelog entry to `CHANGES.rst`** - This is required and enforced by CI
2. Add a test which proves your fix and make it pass  
3. Add yourself to `docs/credits.rst`

### Changelog entry format

Add your entry under the appropriate section in `CHANGES.rst`:

- **Minor changes:** For small improvements, refactoring, documentation updates
- **Breaking changes:** For changes that break existing API
- **New features:** For new functionality
- **Bug fixes:** For bug fixes and error corrections

Example:

```
Minor changes:

- Fix issue with timezone parsing in special cases. See `Issue XXX <link>`_.
```

## Setup for development

If you would like to setup icalendar to contribute changes, the [Installation Section](https://icalendar.readthedocs.io/en/latest/install.html) should help you further.