#!/usr/bin/env bash
set -eu
cp -RL "$(dirname "$0")/files/." .
bash ./build.sh
rm build.sh lib.sh
