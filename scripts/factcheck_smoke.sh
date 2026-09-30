#!/usr/bin/env bash
# Smoke test for IOW-007: the key works and returns ClaimReview items.
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; [ -f .env ] && . ./.env; set +a
: "${GOOGLE_FACTCHECK_API_KEY:?set it in .env}"
curl -fsS -G 'https://factchecktools.googleapis.com/v1alpha1/claims:search' \
  --data-urlencode 'query=India' --data-urlencode 'languageCode=en' \
  --data-urlencode 'pageSize=5' --data-urlencode "key=${GOOGLE_FACTCHECK_API_KEY}" |
python3 -c '
import json, sys
claims = json.load(sys.stdin).get("claims", [])
assert claims, "no claims returned"
for c in claims:
    print(c["claimReview"][0]["publisher"]["name"], "|", c["text"][:80])
'
