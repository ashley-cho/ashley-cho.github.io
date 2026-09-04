#!/usr/bin/env bash
# Rebuild the Data Center Power Atlas from source data.
#
#   ./tools/atlas/refresh.sh
#
# Runs the three stages in order and writes the finished page to
# public/datacenters/index.html. Any stage failing stops the run, so a
# broken build never overwrites a working page.
set -euo pipefail
cd "$(dirname "$0")"

python3 build/build.py      # sites.py -> build/entities.json  (geocode, grid factors)
python3 build/gen.py        # entities + JSON sources -> build/data.json
python3 assemble.py         # data + parts -> dist/index.html

repo="$(git -C . rev-parse --show-toplevel)"
mkdir -p "$repo/public/datacenters"
cp dist/index.html "$repo/public/datacenters/index.html"
echo "public/datacenters/index.html updated ($(wc -c < dist/index.html | tr -d ' ') bytes)"
