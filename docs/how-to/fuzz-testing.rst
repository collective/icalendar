============
Fuzz testing
============

This chapter describes how to perform automated fuzz testing.

`Fuzz testing or fuzzing <https://en.wikipedia.org/wiki/Fuzzing>`_ is an automated software testing technique that involves providing invalid, unexpected, or random data as inputs to a computer program.
The program is then monitored for exceptions such as crashes, failing built-in code assertions, or potential memory leaks.

icalendar uses `OSS-Fuzz`_ and `GitHub Actions <https://github.com/collective/icalendar/actions/workflows/cifuzz.yml>`_ for fuzz testing.


Identify uncaught fuzzing errors
================================

Occasionally, fuzz testing creates uncaught errors for which icalendar needs a test case.

In a GitHub Actions log, calendars are printed out as base64-encoded lines of text with a leading timestamp.
A sample log file is available at :download:`fuzz-testing-log.txt`.
The following examples come from that log file.
For simplicity, the timestamp is omitted.

A typical calendar example consists of a start and end delimiter surrounding the base64 encoded calendar as shown.

.. code-block:: text

    --- start calendar ---
    QkVHSU46CkJpaWloOgpCaWlpMDoKRU5kOg==
    --- end calendar ---

To decode this calendar, use the following command.

.. code-block:: shell

    $ echo "QkVHSU46CkJpaWloOgpCaWlpMDoKRU5kOg==" | base64 -d

Observe all kinds of random data in the output that the fuzzer generates, and which may trigger errors.

.. code-block:: console

    BEGIN:
    Biiih:
    Biiih0:
    END:

When fuzz testing fails, it appears as an error in the log file.
To identify uncaught fuzzing errors for which icalendar needs a test case, look for a start delimiter, followed by the base64 encoded calendar, and finally a line with an error code followed by the text ``libFuzzer: fuzz target exited``.

.. code-block:: console

    --- start calendar ---
    QkVHSU46VgpSUlVMRTolbjtCWU1PTlRIPQ==
    ==28== ERROR: libFuzzer: fuzz target exited


Create a fuzz test case
=======================

To create the fuzz test case locally, use the following template, filling in the ``<base64>`` string and adding a descriptive ``<filename>``.

.. code-block:: console

    echo "<base64>" | base64 -d | tee src/icalendar/tests/calendars/fuzz_testcase_<filename>.ics

Then, you can run the tests and see that the error is reproduced.

.. code-block:: console

    tox -e py313 -- src/icalendar/tests/fuzzed/

Ignore valid errors.
Fix invalid errors.


Reproduction example
--------------------

In the sample log file :download:`fuzz-testing-log.txt`, find the fuzz test error by searching for the string ``libFuzzer: fuzz target exited``.
Copy the immediately preceding base64 encoded calendar.

.. code-block:: console

    QkVHSU46VgpSUlVMRTolbjtCWU1PTlRIPQ==

The log shows the Python traceback usually a few hundred lines above this calendar.

.. code-block:: text

    --- start calendar ---
    === Uncaught Python exception: ===
    ValueError: Invalid month: ''
    Traceback (most recent call last):

This provides a clue for how to write a test case.
Generate the test case file by running the following command from the root of the repository, using the copied calendar.

.. code-block:: console

    $ echo "QkVHSU46VgpSUlVMRTolbjtCWU1PTlRIPQ==" | base64 -d | tee src/icalendar/tests/calendars/fuzz_testcase_invalid_month.ics
    BEGIN:V
    RRULE:%n;BYMONTH=

Next, run the tests.

.. code-block:: shell

    $ tox -e py313 -- src/icalendar/tests/fuzzed/

The output shows that the error is reproduced.

.. code-block:: console

    src/icalendar/tests/fuzzed/test_fuzzed_calendars.py .F
    # ...
    ValueError: Invalid month: ''

Some tests cases point to code to fix.
This one points to a valid error for a wrong month value.
An empty month is invalid by the specification.
As such, it is correct to have this error.
Commit the test case and push it to a pull request, so that the error can be safely ignored during fuzz testing.


Reproduce fuzzing issues locally
================================

To reproduce fuzzing issues locally, install `OSS-Fuzz`_ locally, following its
`setup instructions <https://google.github.io/oss-fuzz/advanced-topics/reproducing/#reproduce-using-local-source-checkout>`_.

Then, you can run the script ``generate_python_test_cases_from_downloaded_clusterfuzz_test_cases.sh``
in ``src/icalendar/tests/fuzzed/`` to generate python test cases from the downloaded fuzzer test cases.

.. code-block:: shell

    src/icalendar/tests/fuzzed/generate_python_test_cases_from_downloaded_clusterfuzz_test_cases.sh

.. _OSS-Fuzz: https://google.github.io/oss-fuzz/
