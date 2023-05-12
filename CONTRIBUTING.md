# Contributing to Superset API Client

## Setting up your development environment

To be written

## Releasing

> This releasing section is intended for releasers only.
> You won't be able to release without permissions.

### Before releasing
To release you will need to install github CLI:
1. Install github CLI following the instructions here: https://github.com/cli/cli#installation
2. Authenticate with `gh auth login` and follow the instructions.

### Creating a new release
To create a new release:
1. Go to master branch and merge develop branch
2. Release using the release script `bash ./scripts/release.sh`
