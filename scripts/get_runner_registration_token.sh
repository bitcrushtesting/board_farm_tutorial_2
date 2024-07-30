#!/bin/bash


ORGANISATION="bitcrushtesting"

echo "Requesting tolen for: ${ORGANISATION}"

gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /orgs/${ORGANISATION}/actions/runners/registration-token
