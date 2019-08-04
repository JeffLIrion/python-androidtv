#!/bin/bash

# get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# get the current version
VERSION_LINE=$(grep '__version__' $DIR/../androidtv/__init__.py)
VERSION_TEMP=${VERSION_LINE%"'"}

LSTRIP="*'"

VERSION=${VERSION_TEMP##$LSTRIP}

# Announce the tag
echo "Creating tag v$VERSION"

cd $DIR/..
git tag v$VERSION -m "v$VERSION"
git push --tags
