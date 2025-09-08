#!/usr/bin/env bash
# Validate required environment variables for MindForge
set -euo pipefail

REQUIRED_VARS=(
  SECRET_KEY
  DATABASE_URL
  GOOGLE_OAUTH_CLIENT_ID
  GOOGLE_OAUTH_CLIENT_SECRET
  GITHUB_OAUTH_CLIENT_ID
  GITHUB_OAUTH_CLIENT_SECRET
  STRIPE_PUBLIC_KEY
  STRIPE_SECRET_KEY
)

missing=()
for var in "${REQUIRED_VARS[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    missing+=("$var")
  fi
done

if (( ${#missing[@]} )); then
  echo "Missing required environment variables: ${missing[*]}" >&2
  exit 1
fi

echo "All required environment variables are set."
