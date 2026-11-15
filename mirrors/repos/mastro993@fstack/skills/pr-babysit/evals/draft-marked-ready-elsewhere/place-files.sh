#!/usr/bin/env bash
set -eu
cp -RL "$(dirname "$0")/files/." .
bash ./setup-fixture.sh
