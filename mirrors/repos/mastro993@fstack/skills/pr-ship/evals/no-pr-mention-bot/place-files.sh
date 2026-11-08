#!/usr/bin/env bash
# The simulated gh and the fixture builder are pr-babysit's, shared by both skills' evals.
set -eu
here=$(dirname "$0")
shared="$here/../../../pr-babysit/evals/ci-failure-fix-and-report/files"
cp -RL "$here/files/." .
mkdir -p bin
cp "$shared/bin/gh" bin/gh
cp "$shared/setup-fixture.sh" .
bash ./setup-fixture.sh
