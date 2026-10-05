#!/usr/bin/env bash
#
# Deploy the CatSight API to Cloud Run.
#
# Takes the project from the environment, never from a literal in this file -
# the rule stated in backend/.env.example. Run `scripts/check_access.ps1`
# first; this script assumes the APIs are enabled and you are authenticated.
#
#   PROJECT_ID=techno-crackers-catsight ./scripts/deploy.sh
#
# Cost guards are applied here rather than left to the console (C-12), so a
# redeploy cannot quietly drop them.

set -euo pipefail

PROJECT_ID="${PROJECT_ID:-${GOOGLE_CLOUD_PROJECT:-}}"
REGION="${REGION:-us-central1}"
SERVICE="${SERVICE:-catsight-api}"
# Gemini 3.x is not served from us-central1, so the model location stays
# global while the service itself runs in the region with the data.
MODEL_LOCATION="${MODEL_LOCATION:-global}"

if [[ -z "${PROJECT_ID}" ]]; then
  echo "PROJECT_ID is not set." >&2
  echo "  PROJECT_ID=techno-crackers-catsight ./scripts/deploy.sh" >&2
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}/backend"

BUCKET="${GCS_BUCKET:-${PROJECT_ID}-docs}"
ORIGINS="${ALLOWED_ORIGINS:-http://localhost:5173,https://${PROJECT_ID}.web.app,https://${PROJECT_ID}.firebaseapp.com}"
BUILD_LABEL="${BUILD_LABEL:-$(git rev-parse --short HEAD 2>/dev/null || echo manual)}"

echo "project ${PROJECT_ID} | region ${REGION} | service ${SERVICE} | build ${BUILD_LABEL}"

# --min-instances 0 so an idle demo costs nothing; --max-instances 3 so a
# popular link cannot run up a bill (C-12). --timeout 300 because an analysis
# streams for longer than the 60s default, and a truncated SSE stream looks
# to a judge like a broken product.
gcloud run deploy "${SERVICE}" \
  --project "${PROJECT_ID}" \
  --region "${REGION}" \
  --source . \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 3 \
  --timeout 300 \
  --cpu 1 \
  --memory 1Gi \
  --concurrency 20 \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
  --set-env-vars "GOOGLE_CLOUD_LOCATION=${MODEL_LOCATION}" \
  --set-env-vars "GOOGLE_GENAI_USE_ENTERPRISE=true" \
  --set-env-vars "GCS_BUCKET=${BUCKET}" \
  --set-env-vars "^|^ALLOWED_ORIGINS=${ORIGINS}" \
  --set-env-vars "BUILD_LABEL=${BUILD_LABEL}"

URL="$(gcloud run services describe "${SERVICE}" \
  --project "${PROJECT_ID}" --region "${REGION}" --format 'value(status.url)')"

echo
echo "Service URL: ${URL}"
echo
echo "Next:"
echo "  1. Put it in frontend/.env.local:  VITE_API_BASE_URL=${URL}"
echo "  2. Verify:                         ./scripts/smoke_test.sh ${URL}"
echo
echo "ALLOWED_ORIGINS was set to the default Hosting domains. If the frontend"
echo "is served from anywhere else, redeploy with ALLOWED_ORIGINS set, or the"
echo "browser will fail CORS with no error in the server logs."
