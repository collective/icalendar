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
-   Address the reader by using "you" and "your" instead of "the user" or "the user's."
-   When giving instructions and in headings, use the `imperative mood of verbs <https://learn.microsoft.com/en-us/style-guide/grammar/verbs#mood-of-verbs>`_.
-   Use the `active voice <https://learn.microsoft.com/en-us/style-guide/grammar/verbs#active-and-passive-voice>`_ whenever possible, avoiding the passive voice.
-   Headings should be "Sentence cased," not "Title Cased."
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


.. _markup-and-formatting:

Markup and formatting
---------------------

When writing documentation, use the `reStructuredText <https://docutils.sourceforge.io/rst.html>`_ markup syntax.

When writing API reference documentation, write `docstrings <https://peps.python.org/pep-0257/#what-is-a-docstring>`_ inside the Python code following the `Google Python Style Guide, Comments and Docstrings <https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings>`_ format.
These docstrings get rendered into the :doc:`API reference documentation <../../reference/api/icalendar>`.

Sphinx and its extensions enhance core reStructuredText with additional features.

-   automatic API documentation file generation in reStructuredText through :mod:`sphinx:sphinx.ext.apidoc`
-   rendering of API documentation files and Python docstrings to HTML through :mod:`sphinx:sphinx.ext.autodoc`, :mod:`sphinx.ext.napoleon`, and `sphinx_autodoc_typehints <https://github.com/tox-dev/sphinx-autodoc-typehints?tab=readme-ov-file>`_
-   rendering of Python source files to HTML through :doc:`sphinx.ext.viewcode <sphinx:usage/extensions/viewcode>`
-   hyperlinking to internal and external documentation through :doc:`sphinx.ext.intersphinx <sphinx:usage/extensions/intersphinx>`
-   display and one-click copying of code blocks through `sphinx_copybutton <https://sphinx-copybutton.readthedocs.io/en/latest/index.html>`_
-   user interface enhancements, including tabular interfaces, cards, and buttons through `sphinx_design <https://sphinx-design.readthedocs.io/en/latest/index.html>`_
-   redirects for moved files through `sphinx_reredirects <https://documatt.com/sphinx-reredirects/usage/>`_
-   404 not found page through `notfound.extension <https://sphinx-notfound-page.readthedocs.io/en/latest/autoapi/notfound/extension/index.html>`_
-   automatic linking to GitHub issues and pull requests through `sphinx-issues <https://github.com/sloria/sphinx-issues>`_

For configuration of these features, see :ref:`configure-a-package`.


Markup examples
---------------

All of the following markup examples will work in both narrative and API documentation.
API documentation has additional syntax usage.


General cross-references
''''''''''''''''''''''''

Sphinx supports various cross-referencing roles to create hyperlinks to other elements in the documentation.

In icalendar's documentation, the most frequently used roles are the following.

-   :rst:role:`doc` to link to a file
-   :rst:role:`ref` to link to an arbitrary label
-   :rst:role:`term` to link to a glossary term
-   :rst:role:`rfc` to link to an RFC
-   ``issue`` or ``pr`` to link to a GitHub issue or pull request, provided by `sphinx-issues <https://github.com/sloria/sphinx-issues>`__

When referencing a specific section in an RFC, copy the anchor name from the URL, that is, the part of the URL including and after the pound sign ``#``, and use the following syntax.

.. code-block:: text

    :rfc:`number#anchor`

The following example shows how to link to RFC 6350, Section 6.2.2.

.. code-block:: rst

    :rfc:`6350#section-6.2.2`

Which renders as shown.

:rfc:`6350#section-6.2.2`

When referencing a GitHub issue, use the following syntax.

.. code-block:: rst

    :issue:`1050`

Which renders as a hyperlink to the issue on GitHub.

:issue:`1050`

Similarly, for a pull request, the syntax would be the following.

.. code-block:: rst

    :pr:`808`

Which renders as a hyperlink to the pull request on GitHub.

:pr:`808`

.. seealso::

    :doc:`sphinx:usage/referencing`
        For general Sphinx cross-referencing.

    `sphinx-issues <https://github.com/sloria/sphinx-issues>`_
        For additional usage examples of the ``issue``, ``pr``, and other GitHub roles.


Cross-reference Python objects
''''''''''''''''''''''''''''''

In addition to the general cross-references, Sphinx supports various cross-referencing roles to create hyperlinks to Python objects.
As with all cross-references, these forms consist of a role, a target, an optional custom label, and an optional modifier.

In icalendar's documentation, the most frequently used roles in the Python domain are the following.

-   :rst:role:`class <py:class>`
-   :rst:role:`mod <py:mod>`
-   :rst:role:`func <py:func>`
-   :rst:role:`attr <py:attr>`

The target must be either a full dotted Python path or use a shortcut to disambiguate to which object it should be hyperlinked.

The following reStructuredText source examples show which form to use to get the preferred display.
These examples are ordered from most to least preferred.

object only
    Use this form only when the object exists in the rendered HTML page.
    Thus the object's context is clear to be that within its Python module or class.
    To do so, use the tilde character ``~`` as a modifier, along with the role and target, to display only the object when rendered.

    .. code-block:: rst

        :class:`~icalendar.prop.vXmlReference`

    The above example will render as shown.

        :class:`~icalendar.prop.vXmlReference`

full dotted Python path
    Use this form only when the object exists outside the rendered HTML page, such as in a superclass.
    To do so, use the following syntax consisting of a role and target only.

    .. code-block:: rst

        :class:`icalendar.prop.vXmlReference`

    The above example will render as shown.

        :class:`icalendar.prop.vXmlReference`

custom text label
    As a compromise to showing the full dotted Python path, while retaining sufficient context of the object's location when displayed, use a custom text label.
    Use this form only when horizontal space is constrained when rendered to HTML.

    .. code-block:: rst

        :class:`prop.vXmlReference <icalendar.prop.vXmlReference>`

    The above example will render as shown.

        :class:`prop.vXmlReference <icalendar.prop.vXmlReference>`

.. seealso::

    :doc:`sphinx:usage/domains/python`

    .. note::

        Because icalendar uses the Python domain exclusively, it's safe to omit the ``:py`` prefix when creating references to Python objects.


Target shortcut
```````````````

As well as the above forms, you can use a shortcut to avoid repeating the full dotted path in the target.
In the page in which the reference appears, you may use the :rst:dir:`currentmodule <py:currentmodule>` directive and omit the name of the current module.

.. code-block:: rst

    .. currentmodule:: icalendar.prop

    The class :class:`vXmlReference` is useful.

.. currentmodule:: icalendar.prop

The above example will render as shown.

    The class :class:`vXmlReference` is useful.


Python docstrings
-----------------

Python docstrings provide clear explanations of what code does, making it easier for people to use and maintain it.
Sphinx generates documentation automatically from docstrings into the :doc:`icalendar API reference guide <../../reference/api/icalendar>`, enhancing code readability and usability.

Python docstrings typically include reStructuredText markup, often including cross-references to narrative and API documentation.

:pep:`257` describes core docstring conventions.
To enhance the display of its API documentation, icalendar uses the Sphinx extensions :mod:`sphinx.ext.napoleon` and `sphinx_autodoc_typehints <https://github.com/tox-dev/sphinx-autodoc-typehints?tab=readme-ov-file>`_.
The former extension supports Google style docstrings, which are easier to write and read, especially when Sphinx renders them to HTML.
The latter extension supports Python 3 annotations, or type hints, for documenting acceptable parameter types and return value types of functions.

.. seealso::

    `Google Python Style Guide <https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings>`_ for more examples of docstrings and their format.


Docstring structure
-------------------

In addition to the structure of docstrings as defined by :pep:`257`, icalendar has adopted conventions from the `Google Python Style Guide <https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings>`_.

A docstring consists of a summary, followed by a possible description, then any helpful sections usually ordered by inputs then outputs.

To create a docstring section, use either one of the supported :ref:`section headers <sphinx:Sections>` or any string for a custom section header, followed by a colon ``:``, followed by a block of indented text.
Supported section headers enhance formatting, such as structuring method parameters or code examples, whereas custom section headers render as just a heading and content.

All items should terminate with a period.

The following docstrings items are the most frequently used in icalendar, although they may be others.

Summary
    Docstrings must begin with a one-line summary of the Python object, terminated by a period.

Description
    When the one-line summary is insufficient to describe the Python object, then write an overall description of what it does, without going into details of how it does it.
    Leave implementation details to the code, and optionally inline code comments.
    Separate the summary and description with a blank line.

``Attributes``
    Each attribute should consist of its name and a brief description.
    By virtue of Sphinx extensions and the use of type hints for the Python object, you may omit the parameter's type, allowing Sphinx to automatically render it for you.

``Parameters``
    Each parameter should consist of its name and a brief description.
    By virtue of Sphinx extensions and the use of type hints for the Python object, you may omit the parameter's type, allowing Sphinx to automatically render it for you.

``Returns``
    The return value consists of its return type and a brief description.

``Raises``
    The ``Raises`` section is a list of all exceptions that are relevant to the interface.

``Examples``
    Usage examples of the Python object.
    These must be valid examples, including imports, as they must pass tests.
    Not only are these helpful to developers, but they're fun to write, and rewarding when they pass.

.. seealso::

    :ref:`sphinx:Sections`


Escape docstrings
-----------------

Avoid double-escaping in docstrings.
Use the raw ``r`` indicator immediately before the leading docstring delimiter ``"""``.
Thus the docstring and the rendered content will have the same level of escapes.
It will also be less confusing for readers of the source code.

.. seealso::

    :ref:`parser-split_on_unescaped_semicolon` example.


Docstring examples
------------------

The following examples are actual docstrings in icalendar that will render properly.

``Event.new()``
'''''''''''''''

See the rendered view of this class method at :meth:`Event.new() <icalendar.cal.event.Event.new>`.

.. literalinclude:: ../../../src/icalendar/cal/event.py
    :pyobject: Event.new


``Component.register``
''''''''''''''''''''''

See the rendered view of this class method at :meth:`Component.register <icalendar.cal.component.Component.register>`.

.. literalinclude:: ../../../src/icalendar/cal/component.py
    :pyobject: Component.register


.. _parser-split_on_unescaped_semicolon:

``parser.split_on_unescaped_semicolon``
'''''''''''''''''''''''''''''''''''''''

See the rendered view of this class method at :meth:`parser.split_on_unescaped_semicolon <icalendar.parser.split_on_unescaped_semicolon>`.

.. literalinclude:: ../../../src/icalendar/parser.py
    :pyobject: split_on_unescaped_semicolon


Style and quality checks
------------------------

When making a contribution to documentation, style and quality checks must pass both locally while developing and in continuous integration after opening a pull request.

.. seealso::

    See :doc:`build-check` for how to set up and run the builds and checks on documentation.

In addition to automated checks, perform visual checks to ensure that documentation renders as intended.

icalendar is configured with Read the Docs to build pull request previews of documentation.
When a pull request is opened on a branch and there are changes to any documentation files, Read the Docs will build a preview of the documentation, and insert a link to the build in the pull request description.
If there's no link, either there are no changes to documentation files or the branch isn't in the icalendar repository.
All pull request preview builds are listed on Read the Docs at `icalendar builds <https://app.readthedocs.org/projects/icalendar/builds/>`_.

Always pay attention to errors and continuous integration failures, and attempt to resolve them.
Warnings may provide helpful information.


Link checks
'''''''''''

All links must be valid.

.. seealso::

    See how to check links in :ref:`make-linkcheckbroken`.


Spelling and grammar
''''''''''''''''''''

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
    See :ref:`vale-configuration` for details.

.. seealso::

    See how to use :ref:`Vale <make-vale>`.

