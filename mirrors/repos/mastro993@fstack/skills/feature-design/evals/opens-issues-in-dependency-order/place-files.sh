#!/usr/bin/env bash
set -eu
here="$(dirname "$0")"
cp -R "$here/../challenges-idea-before-interview/files/." .
cp -R "$here/files/." .
git -C readwell init -q -b main
git -C readwell remote add origin https://github.com/millbrook/readwell.git
git -C readwell add -A
git -C readwell -c user.name=fixture -c user.email=fixture@example.org commit -qm "Readwell with the email-renewals spec"
