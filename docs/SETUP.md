# CatSight: complete infrastructure and credentials setup

> Do this **once**, before or alongside phase P0. It takes about 45–60 minutes.
>
> **Run the GCP commands in Google Cloud Shell** (https://shell.cloud.google.com). It is bash, comes with gcloud and is already logged in. Local Windows PowerShell 5.1 breaks some gcloud JSON flags.
>
> **Where these commands came from:** EXECUTION_PLAN §3 (updated with the research findings).

---

## 0. What credentials do we actually need?

| Credential | Needed? | Where it lives |
|---|---|---|
| Gemini API key | **No.** Gemini is called through Agent Platform (Vertex) using the Cloud Run **service account**. The $300 trial credit **doesn't cover** AI Studio API keys. | — |
| GCP service account `catsight-run` | **Yes** (created in §4) | Attached to Cloud Run; no key file |
| Local developer credentials | **Yes** | `gcloud auth application-default login` on each laptop |
| `ADMIN_TOKEN` (protects `/api/admin/ingest`) | **Yes** | Secret Manager → Cloud Run env |
| Firebase CLI login | **Yes** | `firebase login` (local or Cloud Shell) |
| GitHub | **Yes** | A fresh **public** repo; your normal git auth |
| AI Studio API key | **Only as a fallback** (Scenario B: no trial eligibility) | Secret Manager, `GEMINI_API_KEY` |

> 🔒 **Never commit:** service-account key files, `.env` files with tokens, or `ADMIN_TOKEN`. Add `.env*` and `*.json` key patterns to `.gitignore`. Key files shouldn't exist at all.

---

## 1. Prerequisites (each developer laptop, Windows)

```powershell
winget install Google.CloudSDK
winget install Python.Python.3.12
winget install OpenJS.NodeJS.LTS
winget install Git.Git
npm install -g firebase-tools
gcloud auth login
gcloud auth application-default login     # lets local Python call Gemini/Firestore as you
```

Restart the terminal after installing, then check the versions:

```powershell
python --version; node --version; gcloud --version; firebase --version
```

## 2. Project and billing (Cloud Shell)

1. In the Console, start the **$300 Free Trial** if you haven't. Then check **Billing → Credits** for the expiry date: it must be **after Dec 4, 2026**. If it isn't, plan to upgrade before expiry; remaining credit carries over but still expires at day 90.

```bash
export PROJECT_ID="techno-crackers-catsight"   # globally unique; change if taken
export REGION="us-central1"
gcloud projects create $PROJECT_ID --name="CatSight"
gcloud billing accounts list
export BILLING_ACCOUNT="XXXXXX-XXXXXX-XXXXXX"
gcloud billing projects link $PROJECT_ID --billing-account=$BILLING_ACCOUNT
gcloud config set project $PROJECT_ID
gcloud config set run/region $REGION
```

2. Add both teammates (team of 3). Use their **real** Google account emails.

   A project with no organization (a personal Gmail account) **can't grant `roles/owner` from the CLI**; you get the error `SOLO_MUST_INVITE_OWNERS`. Grant these roles instead:

```bash
for U in teammate1@gmail.com teammate2@gmail.com; do
  for ROLE in roles/editor roles/iam.serviceAccountUser roles/run.admin roles/secretmanager.admin roles/firebase.admin; do
    gcloud projects add-iam-policy-binding $PROJECT_ID --member="user:$U" --role=$ROLE --condition=None
  done
done
```

   For Owner, use Console → IAM & Admin → IAM → Grant access → Owner. The invitee must accept the emailed invitation.

## 3. Enable APIs

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com aiplatform.googleapis.com firestore.googleapis.com \
  storage.googleapis.com secretmanager.googleapis.com logging.googleapis.com \
  cloudtrace.googleapis.com firebase.googleapis.com firebasehosting.googleapis.com \
  billingbudgets.googleapis.com iamcredentials.googleapis.com
```

## 4. Service account and IAM

```bash
gcloud iam service-accounts create catsight-run --display-name="CatSight Cloud Run SA"
export SA="catsight-run@$PROJECT_ID.iam.gserviceaccount.com"
for ROLE in roles/aiplatform.user roles/datastore.user roles/storage.objectAdmin \
            roles/logging.logWriter roles/cloudtrace.agent roles/secretmanager.secretAccessor \
            roles/iam.serviceAccountTokenCreator; do
  gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA" --role=$ROLE --condition=None
done
```

`serviceAccountTokenCreator` lets the service account sign the GCS URLs used by "view PDF page" links.

## 5. Data stores

```bash
gcloud firestore databases create --location=$REGION --type=firestore-native
gcloud storage buckets create gs://$PROJECT_ID-docs --location=$REGION --uniform-bucket-level-access

# Vector index (gcloud only: the Firebase CLI has a vector-index bug)
gcloud firestore indexes composite create --collection-group=treaty_chunks \
  --query-scope=COLLECTION --field-config=order=ASCENDING,field-path=treaty_id \
  --field-config='field-path=embedding,vector-config={"dimension":"768","flat":"{}"}' \
  --database="(default)"
gcloud firestore indexes composite list     # wait until STATE = READY
```

## 6. Secrets

```bash
openssl rand -hex 24 | gcloud secrets create ADMIN_TOKEN --data-file=-
# Fallback only (no trial): echo -n "AIza..." | gcloud secrets create GEMINI_API_KEY --data-file=-
```

The value isn't printed, because it goes straight into Secret Manager. No file is created and none is needed; Cloud Run reads the secret directly. To see the value (for manual admin calls or local testing), run `gcloud secrets versions access latest --secret=ADMIN_TOKEN`. Keep it in a password manager, never in the repo.

## 7. Cost guardrails (do this before writing code)

```bash
gcloud billing budgets create --billing-account=$BILLING_ACCOUNT \
  --display-name="catsight-budget" --budget-amount=6000INR \
  --threshold-rule=percent=0.25 --threshold-rule=percent=0.5 --threshold-rule=percent=0.9
```

**Our billing account is in INR.** The trial started **2026-10-02** with ₹28,796.63 of credit (≈ $300) for 90 days, so it **expires around 2026-12-31**, after the Dec 4 finale. Set budgets and caps in INR.

**Spend caps (Preview, Console):** Billing → Budgets & alerts → create a spend cap for **Agent Platform (about ₹4,000/month)** and **Cloud Run (about ₹2,000/month)** on this project. Caps count **gross** cost (credits ignored) and pause the service when hit.

## 8. Verify Gemini access (local PowerShell)

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install "google-genai>=2.19,<3"
python -c "from google import genai; c=genai.Client(enterprise=True, project='techno-crackers-catsight', location='global'); [print(m, '->', c.models.generate_content(model=m, contents='Reply OK').text) for m in ('gemini-3.5-flash-lite','gemini-3.8-flash')]"
python -c "from google import genai; from google.genai import types; c=genai.Client(enterprise=True, project='techno-crackers-catsight', location='global'); r=c.models.embed_content(model='gemini-embedding-001', contents='test', config=types.EmbedContentConfig(output_dimensionality=768)); print(len(r.embeddings[0].values))"
```

Expected output: two "OK" replies and `768`. If `enterprise=True` errors, use `vertexai=True`. A 404 means the location isn't `global`.

## 9. Firebase

> **Recommended path:** a new Firebase account gets **403 PERMISSION_DENIED** from `addfirebase` until it accepts Firebase's terms in the browser. Go to **console.firebase.google.com** → Add project → select the existing `techno-crackers-catsight` project → confirm Blaze → turn Analytics **off**. Then check with `firebase projects:list`.

```bash
firebase login --no-localhost     # in Cloud Shell
firebase projects:addfirebase $PROJECT_ID   # only works once the terms are accepted; the Console route above is easier
# in the repo root, after the frontend exists:
firebase use $PROJECT_ID
firebase init hosting     # public dir: frontend/dist, SPA: yes, no GitHub action (optional)
```

The live URL will be `https://$PROJECT_ID.web.app`.

## 10. Artifact Registry cleanup (after the first deploy creates the repo)

```bash
cat > cleanup.json <<'EOF'
[{"name":"keep-recent","action":{"type":"Keep"},"mostRecentVersions":{"keepCount":3}},
 {"name":"delete-old","action":{"type":"Delete"},"condition":{"olderThan":"7d"}}]
EOF
gcloud artifacts repositories set-cleanup-policies cloud-run-source-deploy --location=$REGION --policy=cleanup.json
```

## 11. Deploy reference (the builder automates this in `scripts/deploy.sh`)

```bash
cd backend
gcloud run deploy catsight-api --source . --region $REGION --service-account $SA \
  --allow-unauthenticated --cpu 1 --memory 1Gi --concurrency 20 --timeout 300 \
  --min-instances 0 --max-instances 3 --cpu-boost \
  --set-env-vars "^;^GOOGLE_GENAI_USE_ENTERPRISE=true;GOOGLE_CLOUD_PROJECT=$PROJECT_ID;GOOGLE_CLOUD_LOCATION=global;MODEL_MAIN=gemini-3.5-flash-lite;MODEL_REASON=gemini-3.8-flash;GCS_BUCKET=$PROJECT_ID-docs;DAILY_ANALYSIS_CAP=300;ALLOWED_ORIGINS=https://$PROJECT_ID.web.app,https://$PROJECT_ID.firebaseapp.com,http://localhost:5173" \
  --set-secrets ADMIN_TOKEN=ADMIN_TOKEN:latest
cd ../frontend
echo "VITE_API_BASE=$(gcloud run services describe catsight-api --region $REGION --format='value(status.url)')" > .env.production
npm run build && cd .. && firebase deploy --only hosting,firestore:rules
```

**Note:** the `^;^` prefix switches the variable separator to `;`. `ALLOWED_ORIGINS` contains commas, and without the prefix gcloud would split on them.

## 12. Local dev environment file (`backend/.env`, git-ignored)

```
GOOGLE_GENAI_USE_ENTERPRISE=true
GOOGLE_CLOUD_PROJECT=techno-crackers-catsight
GOOGLE_CLOUD_LOCATION=global
GCS_BUCKET=techno-crackers-catsight-docs
MODEL_MAIN=gemini-3.1-flash-lite
MODEL_REASON=gemini-3.8-flash
ADMIN_TOKEN=local-dev-only
ALLOWED_ORIGINS=http://localhost:5173
```

`gemini-3.1-flash-lite` is the cheaper model for local development.

## 12a. Teammate onboarding (each additional developer)

Teammates use **their own Google account**. Nobody shares keys or passwords. Access comes from the IAM roles granted in §2.

**What the project owner shares** (non-secret; put it in the team chat):

| Value | Ours |
|---|---|
| `PROJECT_ID` | `techno-crackers-catsight` |
| `REGION` | `us-central1` (Cloud Run, Firestore, GCS) |
| `GOOGLE_CLOUD_LOCATION` | `global` (Gemini) |
| `GCS_BUCKET` | `techno-crackers-catsight-docs` (or whatever you actually created) |
| Service account | `catsight-run@techno-crackers-catsight.iam.gserviceaccount.com` |
| Live URL (after the first deploy) | `https://techno-crackers-catsight.web.app` |
| GitHub repo | Add the teammate as a **collaborator** (repo Settings → Collaborators) |

**What the teammate runs once on their laptop:**

```powershell
# tools: see §1 (gcloud, Python 3.12, Node LTS, Git, firebase-tools)
gcloud auth login                                   # their own account
gcloud config set project techno-crackers-catsight
gcloud auth application-default login               # lets local code call Gemini/Firestore as them
gcloud auth application-default set-quota-project techno-crackers-catsight
firebase login
git clone <repo-url>; cd catsight
# create backend/.env from the template in §12 (git-ignored)
```

Optionally, they can fetch the admin token themselves (they have Secret Manager access): `gcloud secrets versions access latest --secret=ADMIN_TOKEN`.

**Verify:** run the §8 Gemini check, with two "OK" replies and `768` expected.

**If they get a 403 somewhere:** for Gemini, check that `roles/editor` was granted (it includes Vertex/Agent Platform access) and that `set-quota-project` ran. For Firebase, they open console.firebase.google.com once to accept the terms.

**Billing:** usage by any teammate is charged to the same project, so it's covered by the trial credit. Budget alerts go only to billing-account admins (you).

## 13. Setup checklist

- [x] Trial active (started 2026-10-02, ₹28,796.63, expires ≈ 2026-12-31, after Dec 4 ✔)
- [ ] Project created, billing linked, teammate added
- [ ] APIs enabled
- [ ] Service account plus roles
- [ ] Firestore database plus bucket plus vector index READY
- [ ] `ADMIN_TOKEN` secret
- [ ] Budget alerts plus spend caps
- [ ] Gemini 3.5 Flash-Lite, 3.8 Flash and embedding (768) verified on `global`
- [ ] Firebase added to the project; `firebase login` done
- [ ] Fresh public GitHub repo created
