#!/usr/bin/env bash
set -eu
cp -R "$(dirname "$0")/files/." .
bash ./setup-fixture.sh
