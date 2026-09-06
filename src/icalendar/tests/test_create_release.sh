#!/bin/bash
#
# Create a release file and test it.
#

set -euo pipefail
cd "`dirname \"$0\"`"
cd "../../.."

# setup clean environment

rm -rf dist

# build the release

uv build
archive=`echo dist/icalendar-*.tar.gz`

# run the checks

if ! [ -f "$archive" ]; then
  echo "ERROR: Cannot find distribution archive '$archive'."
  exit 1
fi

FILES="`tar -tf \"$archive\" | grep -o '/.*'`"
ROOT_ENTRIES="`printf '%s\n' "$FILES" | sed 's#^/##; s#/.*##; /^$/d' | LC_ALL=C sort -u`"
EXPECTED_ROOT_ENTRIES="`cat <<'EOF'
.gitignore
LICENSE.rst
Makefile
PKG-INFO
README.rst
docs
funding.json
news
pyproject.toml
src
EOF
`"

if [ "$ROOT_ENTRIES" != "$EXPECTED_ROOT_ENTRIES" ]; then
  echo "ERROR: Source distribution root entries differ from the reviewed allowlist."
  diff -u <(printf '%s\n' "$EXPECTED_ROOT_ENTRIES") <(printf '%s\n' "$ROOT_ENTRIES") || true
  exit 1
fi

if echo "$FILES" | grep -q '^/src/icalendar/fuzzing'; then
  echo "ERROR: Fuzzing files are included in the release."
  echo "       See https://github.com/collective/icalendar/pull/569"
  exit 1
fi

if ! echo "$FILES" | grep -q '^/docs/'; then
  echo "ERROR: The documentation is not included in the release, but should be."
  echo "       See https://github.com/collective/icalendar/issues/712"
  exit 1
fi

if ! echo "$FILES" | grep -q '/funding.json$'; then
  echo "ERROR: Funding files need to be included in the release files."
  echo "       See https://github.com/collective/icalendar/issues/1493"
  exit 1
fi

uvx twine check dist/*

echo "Checks passed."
