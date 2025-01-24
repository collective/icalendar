Security Policy
===============

This documents the security policy and actions to take to secure the package and its deployment and use.

Supported Versions
------------------

Security vulnerabilities are fixed only for the latest version of ``icalendar``.

.. list-table:: Versions to receive security updates
   :widths: 25 25
   :header-rows: 1

   * - Version
     - Supported
   * - 6.*
     - YES
   * - 5.*
     - no
   * - 4.*
     - no
   * - before 4.*
     - no


Reporting a Vulnerability
-------------------------

To report security issues of ``collective/icalendar``, use the ``Report a vulnerability`` button on the project's `Security Page <https://github.com/collective/icalendar/security>`_.
If you cannot do this, please contact one of the :ref:`maintainers` directly.

The maintainers of ``icalendar`` will then notify `Plone's security team <https://plone.org/security/report>`_.

If we determine that your report may be a security issue with the project, we may contact you for further information.
We volunteers ask that you delay public disclosure of your report for at least ninety (90) days from the date you report it to us.
This will allow sufficient time for us to process your report and coordinate disclosure with you.

Once verified and fixed, the following steps will be taken:

-   We will use GitHub's Security Advisory tool to report the issue.
-   GitHub will review our Security Advisory report for compliance with Common Vulnerabilities and Exposures (CVE) rules.
    If it is compliant, they will submit it to the MITRE Corporation to generate a `CVE <https://www.cve.org/>`_.
    This in turn submits the CVE to the `National Vulnerability Database (NVD) <https://nvd.nist.gov/vuln/search>`_.
    GitHub notifies us of their decision.
-   Assuming it is compliant, we then publish `our Security Advisory <https://github.com/collective/icalendar/security/advisories>`_ on GitHub, which triggers the next steps.
-   GitHub will publish the CVE to the CVE List.
-   GitHub will broadcast our Security Advisory via the `GitHub Advisory Database <https://github.com/advisories>`_.
-   GitHub will send `security alerts <https://docs.github.com/en/code-security/supply-chain-security/managing-vulnerabilities-in-your-projects-dependencies/about-alerts-for-vulnerable-dependencies>`_ to all repositories that use our package (and have opted into security alerts).
    This includes Dependabot alerts.
-   We will make a bug-fix release.
-   We will send an announcement through our usual channels:

    - The :ref:`Changelog`
    - The GitHub releases of ``icalendar``
    - If possible also `Plone's Security Announcements <https://plone.org/security/announcements>`_

-   We will provide credit to the reporter or researcher in the vulnerability notice.
