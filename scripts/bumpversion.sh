#!/bin/bash

# Make sure there is only 1 argument passed
if [ "$#" -ne 1 ]; then
    echo "You must provide a new version"
    exit 1
fi

# Make sure the new version is not empty
if [ -z "$1" ]; then
    echo "You must provide a non-empty version"
    exit 1
fi

# get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# get the current version
VERSION_LINE=$(grep '__version__' $DIR/../androidtv/__init__.py)
VERSION_TEMP=${VERSION_LINE%"'"}

LSTRIP="*'"

VERSION=${VERSION_TEMP##$LSTRIP}

# Announce the version bump
echo "Bumping the version from $VERSION to $1"

# __init__.py
sed -i "s|__version__ = '$VERSION'|__version__ = '$1'|g" $DIR/../androidtv/__init__.py

# setup.py
sed -i "s|version='$VERSION',|version='$1',|g" $DIR/../setup.py

# conf.py
sed -i "s|version = '$VERSION'|version = '$1'|g" $DIR/../docs/source/conf.py
sed -i "s|release = '$VERSION'|release = '$1'|g" $DIR/../docs/source/conf.py
