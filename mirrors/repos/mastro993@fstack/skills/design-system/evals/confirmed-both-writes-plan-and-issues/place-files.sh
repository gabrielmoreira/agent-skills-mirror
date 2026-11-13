#!/usr/bin/env bash
set -eu
cp -R "$(dirname "$0")/files/." .
cd acme-dash
git init -q -b main
git add -A
git -c user.name=acme -c user.email=dev@acme.test commit -qm "acme-dash before the design system"
