=================
Fuzzing icalendar
=================

We use `OSS-Fuzz`_ to find unforseen errors in icalendar.

The following sections should explain more how to cope with that technology.

How to create a fuzzing test case from GitHub Actions
=====================================================

When you look at a `GitHub Actions <https://github.com/collective/icalendar/actions/workflows/cifuzz.yml>`_ log, you will find that calendars are printed out, base64 encoded.

.. code-block:: text

    --- start calendar ---
    QkVHSU46CkJpaWloOgpCaWlpMDoKRU5kOg==
    --- end calendar ---

Decoding such a calendar, you can see that the fuzzer adds all kinds of random data that trigger errors.

.. code-block:: console

    $ echo "QkVHSU46CkJpaWloOgpCaWlpMDoKRU5kOg==" | base64 -d
    BEGIN:
    Biiih:
    Biiih0:
    END:

The test case that produces the error is **the last test case without** ``--- end calendar ---``, just before ``libFuzzer: fuzz target exited``.

To create the test case locally, use this template, filling in the ``<base64>`` string and adding a descriptive ``<filename>``.

.. code-block:: console

    echo "<base64>" | base64 -d | tee src/icalendar/tests/calendars/fuzz_testcase_<filename>.ics

Then, you can run the tests and see that the error is reproduced:

.. code-block:: console

    tox -e py313 -- src/icalendar/tests/fuzzed/

Valid errors should be ignored. Invalid errors should be fixed.

Reproduction example
--------------------

If you have a look at the :ref:`fuzzing-log`, you can find the string ``QkVHSU46VgpSUlVMRTolbjtCWU1PTlRIPQ==`` as the last calender before 
``libFuzzer: fuzz target exited``.
The log shows the traceback somewhere up top.

.. code-block:: text

    --- start calendar ---
    === Uncaught Python exception: ===
    ValueError: Invalid month: ''
    Traceback (most recent call last):

But the calendar is actually the last one printed.
The test case file is generated with the code:

.. code-block:: console

    $ echo "QkVHSU46VgpSUlVMRTolbjtCWU1PTlRIPQ==" | base64 -d | tee src/icalendar/tests/calendars/fuzz_testcase_invalid_month.ics
    BEGIN:V
    RRULE:%n;BYMONTH=

Then, you can run the tests and see that the error is reproduced:

.. code-block:: console

    $ tox -e py313 -- src/icalendar/tests/fuzzed/
    ...
    src/icalendar/tests/fuzzed/test_fuzzed_calendars.py .F 
    ...
    ValueError: Invalid month: ''
    ...

Some tests cases show us code to fix. This one shows us a valid error for a wrong month value.
An empty month is invalid by the sepcification. As such, it is right to have this error and it should be ignored.

How to reproduce fuzzing issues locally
=======================================

To reproduce fuzzing issues locally, you need to install `OSS-Fuzz`_ locally, following the
`setup instructions <https://google.github.io/oss-fuzz/advanced-topics/reproducing/#reproduce-using-local-source-checkout>`.

Then, you can run the script ``generate_python_test_cases_from_downloaded_clusterfuzz_test_cases.sh``
in ``src/icalendar/tests/fuzzed/`` to generate python test cases from the downloaded fuzzer test cases.

.. _OSS-Fuzz: https://google.github.io/oss-fuzz/

