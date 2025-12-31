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

Sphinx and its extensions enhance core reStructuredText with additional features.

-   automatic API documentation file generation in reStructuredText through :doc:`sphinx:man/sphinx-apidoc`
-   rendering of API documentation files and Python docstrings to HTML through :doc:`sphinx.ext.apidoc <sphinx:usage/extensions/autodoc>`, :doc:`sphinx.ext.napoleon <sphinx:usage/extensions/napoleon>`, and `sphinx_autodoc_typehints <https://github.com/tox-dev/sphinx-autodoc-typehints?tab=readme-ov-file>`_
-   rendering of Python source files to HTML through :doc:`sphinx.ext.viewcode <sphinx:usage/extensions/viewcode>`
-   hyperlinking to internal and external documentation through :doc:`sphinx.ext.intersphinx <sphinx:usage/extensions/intersphinx>`
-   display and one-click copying of code blocks through `sphinx_copybutton <https://sphinx-copybutton.readthedocs.io/en/latest/index.html>`_
-   user interface enhancements, including tabular interfaces, cards, and buttons through `sphinx_design <https://sphinx-design.readthedocs.io/en/latest/index.html>`_
-   redirects for moved files through `sphinx_reredirects <https://documatt.com/sphinx-reredirects/usage/>`_
-   404 not found page through `notfound.extension <https://sphinx-notfound-page.readthedocs.io/en/latest/autoapi/notfound/extension/index.html>`_
.. -   documentation coverage reporting of Python source files through :doc:`sphinx.ext.coverage <sphinx:usage/extensions/coverage>`
.. -   doctest reporting of Python docstring and narrative documentation code examples through :doc:`sphinx.ext.doctest <sphinx:usage/extensions/doctest>`

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

.. seealso::

    :doc:`sphinx:usage/referencing`


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

full dotted Python path
    Use the following syntax consisting of a role and target only.

    .. code-block:: rst

        :class:`icalendar.prop.vXmlReference`

    The above example will render as shown.

        :class:`icalendar.prop.vXmlReference`

object only
    Use the tilde character ``~`` as a modifier, along with the role and target, to display only the object when rendered.

    .. code-block:: rst

        :class:`~icalendar.prop.vXmlReference`

    The above example will render as shown.

        :class:`~icalendar.prop.vXmlReference`

custom text label
    As a compromise to showing the full dotted Python path, while retaining sufficient context of the object's location when displayed, use a custom text label.

    .. code-block:: rst

        :class:`prop.vXmlReference <icalendar.prop.vXmlReference>`

    The above example will render as shown.

        :class:`prop.vXmlReference <icalendar.prop.vXmlReference>`

The form to use depends on the context of the narrative text.
If it's obvious that the object is within the current class or module, then the object only form may be best.
If it's unclear where the object is located, then the full dotted Python path or custom display forms may be better.
Use your best judgment.

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

In icalendar's documentation, the most frequently used roles in the Python domain are the following.

-   :rst:role:`class <py:class>`
-   :rst:role:`mod <py:mod>`
-   :rst:role:`func <py:func>`
-   :rst:role:`attr <py:attr>`

.. seealso::

    :doc:`sphinx:usage/domains/python`

    .. note::

        Because icalendar uses the Python domain exclusively, it's safe to omit the ``:py`` prefix when creating references to Python objects.


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
    See :ref:`vale-configuration` for details.

.. seealso::

    See how to use :ref:`Vale <make-vale>`.

