#!/bin/sh
#
# Create a release file and test it.
#

set -e
cd "`dirname \"$0\"`"
cd "../../.."

python3 setup.py sdist
archive=`echo dist/icalendar-*.tar.gz`

if ! [ -f "$archive" ]; then
  echo "ERROR: Cannot find distribution archive '$archive'."
  exit 1
fi

if tar -tf "$archive" | grep 'fuzzing/'; then
  echo "ERROR: Fuzzing files are included in the release."
  echo "       See https://github.com/collective/icalendar/pull/569"
  exit 1
fi

echo "Checks passed."
