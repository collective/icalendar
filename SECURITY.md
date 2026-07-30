# Security policy

This security policy describes how to privately report _potential_ security issues with icalendar, and how the icalendar security team processes reports, all in a responsible manner.
If you're unsure whether your issue qualifies as a security vulnerability, it's better to err on the side of caution and report it as one, allowing the icalendar security team to evaluate its merits and determine whether it's one.

-   [Report a _potential_ security issue](https://github.com/collective/icalendar/security/advisories/new).
-   [Security advisories](https://github.com/collective/icalendar/security/advisories)


## Supported versions

Security vulnerabilities are fixed only for the latest version of icalendar.
It is highly recommended to upgrade to the latest release.

## Procedure

The icalendar security team will coordinate with the [Plone security team](https://plone.org/security/report).

If it's determined that your report may be a security vulnerability with the project, the team may contact you for further information.
As volunteers, the team asks that you delay public disclosure of your report for at least ninety (90) days from the date you report it to the team.
This will allow sufficient time for the team to process your report and coordinate disclosure with you.

Once verified and fixed, the following steps will be taken:

-   The team will use GitHub's Security Advisory tool to report the vulnerability.
-   GitHub will review the Security Advisory report for compliance with Common Vulnerabilities and Exposures (CVE) rules.
    If it is compliant, they will submit it to the MITRE Corporation to generate a [CVE](https://www.cve.org/).
    This in turn submits the CVE to the [National Vulnerability Database (NVD)](https://nvd.nist.gov/vuln/search).
    GitHub notifies the team of their decision.
-   Assuming it is compliant, the team then publishes the [Security Advisory](https://github.com/collective/icalendar/security/advisories) on GitHub, which triggers the next steps.
-   GitHub will publish the CVE to the CVE List.
-   GitHub will broadcast the Security Advisory via the [GitHub Advisory Database](https://github.com/advisories).
-   GitHub will send [security alerts](https://docs.github.com/en/code-security/supply-chain-security/managing-vulnerabilities-in-your-projects-dependencies/about-alerts-for-vulnerable-dependencies) to all repositories that use icalendar and have opted into security alerts.
    This includes Dependabot alerts.
-   The team will make a bug-fix release.
-   The team will send an announcement through the usual channels:

    - the [change log](https://github.com/collective/icalendar/CHANGES.rst)
    - the [GitHub releases of icalendar](https://github.com/collective/icalendar/releases)
    - [icalendar Discussions Announcements](https://github.com/collective/icalendar/discussions/categories/announcements)
    - [icalendar Open Collective conversations](https://opencollective.com/python-icalendar/conversations)
    - [Plone's Security Announcements](https://plone.org/security/announcements)
    - [Plone Community Forum Announcements](https://community.plone.org/c/announcements/27)

-   The icalendar security team will provide credit to the reporter or researcher in the vulnerability notice.
