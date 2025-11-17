# Makefile for Sphinx documentation
.DEFAULT_GOAL   = help
SHELL           = bash

# You can set these variables from the command line.
SPHINXOPTS      ?=
PAPER           ?=

# Internal variables.
SPHINXBUILD     = "$(realpath .venv/bin/sphinx-build)"
SPHINXAUTOBUILD = "$(realpath .venv/bin/sphinx-autobuild)"
SPHINXAPIDOC   = "$(realpath .venv/bin/sphinx-apidoc)"
DOCS_DIR        = ./docs/
BUILDDIR        = ../_build
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .
VALEFILES       := $(shell find $(DOCS_DIR) -type f -name "*.rst" -print)  # Also add `src` for docstrings.
VALEOPTS        ?=
PYTHONVERSION   = >=3.11,<3.14

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
.PHONY: help
help:  # This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


# environment management
.venv:  ## Install required Python, create Python virtual environment, and install package requirements
	@uv python install "$(PYTHONVERSION)"
	@uv venv --python "$(PYTHONVERSION)"
	@uv sync --group docs

.PHONY: sync
sync:  ## Sync package requirements
	@uv sync

.PHONY: init
init: clean clean-python .venv docs  ## Clean docs build directory and initialize Python virtual environment

.PHONY: clean
clean:  ## Clean docs build directory
	cd $(DOCS_DIR) && rm -rf $(BUILDDIR)/

.PHONY: clean-python
clean-python: clean
	rm -rf .venv/
# /environment management


# documentation builders
.PHONY: html
html: .venv  ## Build html
	cd $(DOCS_DIR) && $(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

.PHONY: livehtml
livehtml: .venv  ## Rebuild Sphinx documentation on changes, with live-reload in the browser
	cd "$(DOCS_DIR)" && ${SPHINXAUTOBUILD} \
		--watch "../src/icalendar/" \
		--watch "../CHANGES.rst" \
		--re-ignore ".*\\.swp|.*\\.typed" \
		--ignore "../src/icalendar/tests" \
		--ignore "../src/icalendar/fuzzing" \
		--port 8050 \
		-b html . "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)

.PHONY: dirhtml
dirhtml: .venv
	cd $(DOCS_DIR) && $(SPHINXBUILD) -b dirhtml $(ALLSPHINXOPTS) $(BUILDDIR)/dirhtml
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/dirhtml."

.PHONY: singlehtml
singlehtml: .venv
	cd $(DOCS_DIR) && $(SPHINXBUILD) -b singlehtml $(ALLSPHINXOPTS) $(BUILDDIR)/singlehtml
	@echo
	@echo "Build finished. The HTML page is in $(BUILDDIR)/singlehtml."

.PHONY: text
text: .venv
	cd $(DOCS_DIR) && $(SPHINXBUILD) -b text $(ALLSPHINXOPTS) $(BUILDDIR)/text
	@echo
	@echo "Build finished. The text files are in $(BUILDDIR)/text."

.PHONY: changes
changes: .venv
	cd $(DOCS_DIR) && $(SPHINXBUILD) -b changes $(ALLSPHINXOPTS) $(BUILDDIR)/changes
	@echo
	@echo "The overview file is in $(BUILDDIR)/changes."
# /documentation builders


# test
.PHONY: linkcheck
linkcheck: .venv  ## Run linkcheck
	cd $(DOCS_DIR) && $(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) $(BUILDDIR)/linkcheck
	@echo
	@echo "Link check complete; look for any errors in the above output " \
		"or in $(BUILDDIR)/linkcheck/ ."

.PHONY: linkcheckbroken
linkcheckbroken: .venv  ## Run linkcheck and show only broken links
	cd $(DOCS_DIR) && $(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) $(BUILDDIR)/linkcheck | GREP_COLORS='0;31' grep -wi "broken\|redirect" --color=always | GREP_COLORS='0;31' grep -vi "https://github.com/plone/volto/issues/" --color=always && if test $$? = 0; then exit 1; fi || test $$? = 1
	@echo
	@echo "Link check complete; look for any errors in the above output " \
		"or in $(BUILDDIR)/linkcheck/ ."

# See https://github.com/collective/icalendar/issues/853 and above comment
.PHONY: vale
vale: .venv  ## Run Vale style, grammar, and spell checks
	@uv run vale sync
	@uv run vale --no-wrap $(VALEOPTS) $(VALEFILES)
	@echo
	@echo "Vale is finished; look for any errors in the above output."

# Not yet implemented
#.PHONY: doctest
#doctest: .venv  ## Test snippets in the documentation
#	cd $(DOCS_DIR) && $(SPHINXBUILD) -b doctest $(ALLSPHINXOPTS) $(BUILDDIR)/doctest
#	@echo "Testing of doctests in the sources finished, look at the " \
#	      "results in $(BUILDDIR)/doctest/output.txt."

.PHONY: test
#test: clean vale linkcheckbroken doctest  ## Clean docs build, then run vale and linkcheckbroken
test: clean linkcheckbroken  ## Clean docs build, then run vale and linkcheckbroken
# /test


# development
.PHONY: apidoc
apidoc: .venv  ## Generate API documentation source files
	cd $(DOCS_DIR) && $(SPHINXAPIDOC) \
 		-f -M -e --remove-old \
 		-o reference/api ../src \
 		../src/icalendar/tests \
 		../src/icalendar/timezone/equivalent_timezone_ids_result.py

.PHONY: all
all: clean linkcheck html  ## Clean docs build, then run linkcheck, and build html
#all: clean vale linkcheck html  ## Clean docs build, then run vale and linkcheck, and build html
# /development

# deployment
.PHONY: rtd-prepare
rtd-prepare:  ## Prepare environment on Read the Docs
	asdf plugin add uv
	asdf install uv latest
	asdf global uv latest

.PHONY: rtd-pr-preview
rtd-pr-preview: rtd-prepare .venv ## Build pull request preview on Read the Docs
	cd $(DOCS_DIR) && $(SPHINXBUILD) -b html $(ALLSPHINXOPTS) ${READTHEDOCS_OUTPUT}/html/
# /deployment
