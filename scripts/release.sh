#!/bin/bash

# This script will release a new version of the package
VERSION=$1

# Confirming release
echo "Releasing version $VERSION, Continue ?"
select yn in "Yes" "No"; do
  case $yn in
    Yes ) break;;
    No ) exit;;
  esac
done

# Creating tag
git tag $VERSION
git push --tags

# Creating release from tag
gh release create $VERSION --generate-notes
