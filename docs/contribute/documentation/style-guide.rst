===========
Style guide
===========

This chapter is the documentation writing style guide for icalendar.
Refer to this guide when you need examples of language, terminology, code, or markup.
It applies to both narrative and API reference documentation.
Differences and exceptions for both types of documentation are noted for each.


Voice and tone
--------------

The icalendar community is warm and friendly, direct and clear, and helpful.
icalendar's documentation reflects its community.

For professional technical documentation writing guidance, the icalendar community selected the `Microsoft Writing Style Guide <https://learn.microsoft.com/en-us/style-guide/welcome/>`_ because it aligns with its spirit.

Key concepts from that guide include the following.

-   Documentation should be informational, but friendly.
-   Address the reader by using "you" and "your" instead of "the user" or "the user's".
-   When giving instructions and in headings, use the `imperative mood of verbs <https://learn.microsoft.com/en-us/style-guide/grammar/verbs#mood-of-verbs>`_.
-   Use the `active voice <https://learn.microsoft.com/en-us/style-guide/grammar/verbs#active-and-passive-voice>`_ whenever possible, avoiding the passive voice.
-   Headings should be "Sentence cased", not "Title Cased".
-   Keep sentences short and understandable.

.. note::
    The style guide is mostly enforced through the use of Vale, but only in the narrative documentation at this time.


Specific guidelines
-------------------

The icalendar developers have adopted additional guidelines.

-   For narrative documentation only, use one sentence per line.
-   For API reference documentation only, line length is automatically enforced by a Python code formatter.
-   Use dashes ``-`` in filenames and avoid underscores ``_``.
-   Images should be no wider than 740 pixels to fit within the documentation's main view port.


Organization and structure
--------------------------

icalendar documentation uses the `Diátaxis framework <https://www.diataxis.fr/>`_, a systematic approach to technical documentation authoring.
Rather than attempt to organize documentation toward a specific role such as developer or user, the Diátaxis framework organizes documentation into the four categories of tutorials, how-to guides, explanation, and reference.
In this way, your title or role does not matter.
Instead, what you want to achieve matters.
By keeping each page focused on one category, readers can focus on getting work done, understanding, or experimenting.


Markup and formatting
---------------------

When writing documentation, use the `reStructuredText <https://docutils.sourceforge.io/rst.html>`_ markup syntax.

When writing API reference documentation, write `docstrings <https://peps.python.org/pep-0257/#what-is-a-docstring>`_ inside the Python code following the `Google Python Style Guide, Comments and Docstrings <https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings>`_ format.
These docstrings get rendered into the :doc:`API reference documentation <../../reference/api/icalendar>`.


Style and quality checks
------------------------

- Sphinx errors and warnings
- Visual checks

  - Local
  - PR previews

- Spelling
- English grammar and Syntax
- Style
- Link check


`Vale <https://vale.sh/>`_ is a linter for narrative text.
It checks spelling, English grammar and syntax, and style guides.
icalendar uses American English.

Because it's difficult to automate good American English grammar and syntax, it's not strictly enforced.
It's understood that contributors might not be fluent in English.
If you're more comfortable writing in your preferred language, then you may submit a pull request written in your language, and the icalendar team will use translation tools to translate it to English.
You're encouraged to make a reasonable effort, and to request a review of their pull request from community members who are fluent in English to fix grammar and syntax.
Please ask!

.. note::
    More corrections to spellings and Vale's configuration are welcome by submitting a pull request.
    This is an easy way to become a contributor to icalendar.
    See :ref:`authors-advanced-vale-usage-label` for details.

.. seealso::

    See how to use :ref:`Vale <make-vale>`.


