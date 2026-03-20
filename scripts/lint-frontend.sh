#!/usr/bin/env bash

set -euo pipefail
set -x

cd team-ui
pnpm tsc -b
pnpm lint
