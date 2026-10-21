# XPO Load Studio — Cloudflare deployment handoff

**Updated:** 2026-10-21  
**Status:** SECRET TYPE VERIFIED / HOSTED LOGIN RETURNS 503 / NEW HIGH-ENTROPY SECRET VALUE REQUIRED / HTTPS ACCEPTANCE BLOCKED  
**Project Route:** [T-016](../TASKS/T-016.md) — BLOCKED (do not mark DONE).

## Current security and runtime finding — 21 October 2026

- Previous risk: XPO_LOGIN_KEY was initially plain_text in dashboard version 42627e7d-60e9-4307-bfe4-16fdbe59c327; historical evidence [audit 39615897041](https://github.com/GabrielValverdeBaez/XPO-Operations/actions/runs/39615897041).
- Remediation confirmed: the latest deployed version f6e3fc63-1e61-4f33-89eb-81277ed7a769 includes XPO_LOGIN_KEY of type **secret_text**; D1, LOGIN_LIMITER and ASSETS are bound. [Audit 39616516566 attempt 2](https://github.com/GabrielValverdeBaez/XPO-Operations/actions/runs/39616516566) PASS. Secret values were never read.
- Bounded HTTPS tests were attempted using only anonymous requests. [Run 39623777257](https://github.com/GabrielValverdeBaez/XPO-Operations/actions/runs/39623777257) exposed Cloudflare 1010 (Python-urllib default browser signature); the security test now sends its own identifiable User-Agent, without disabling Cloudflare browser protections.
- [Run 39624439731](https://github.com/GabrielValverdeBaez/XPO-Operations/actions/runs/39624439731) reached the Worker but observed GET /login HTTP 503. The Worker returned its generic detail for a **missing or invalid runtime key value**. Metadata cannot establish that the value meets key_valid: Python str, length 32..512, at least 12 distinct characters. The runner never received or exposed the secret.
- All temporary tests successfully **restored production workers.dev OFF and previews OFF** via a finally/fail-closed cleanup, so no active public route exists.

**Operator action:** generate a fresh high-entropy password (recommended 48 or more random characters; at least 12 distinct) using a trusted password manager, store it in Cloudflare Production as the **Secret** named exactly XPO_LOGIN_KEY and save/deploy the secret version. Do not reveal the value through GitHub, logs, chat or screenshots. Remove any unused XPO_LOGIN_KEY1 Text variable left from initial setup. No need to recreate D1, the Worker or the deployment API token.

**Next verification:** rerun [bounded HTTPS smoke](../.github/workflows/xpo-cloudflare-private-smoke.yml), which temporarily enables production workers.dev, tests GET /login and anonymous rejection of protected assets/APIs, then disables the route automatically. If the newly generated secret still results in 503, diagnose SDK/runtime binding semantics without weakening the key validity rule.

**T-016 remains BLOCKED** pending real login, HTTPS and D1 persistence acceptance. No operational data or authenticated login was tested.
## 1. Canonical deployment baseline

Repository: [GabrielValverdeBaez/XPO-Operations](https://github.com/GabrielValverdeBaez/XPO-Operations)  
Deployment branch: `feat/cloudflare-deployment`  
Pull request: [#4](https://github.com/GabrielValverdeBaez/XPO-Operations/pull/4) (draft, not merged)  
Deploy workflow: [xpo-cloudflare-deploy.yml](../.github/workflows/xpo-cloudflare-deploy.yml)  
Read-only audit workflow: [xpo-cloudflare-audit.yml](../.github/workflows/xpo-cloudflare-audit.yml)

Existing, dedicated Cloudflare resources (do **not** recreate or reuse Evenio resources):

| Resource | Identifier |
|---|---|
| Account | `0054188c07d3b5fe7cb20fc4f71dc212` |
| Worker | `xpo-load-studio` (ID `9f213a235e0f402a99631cc17c4a37af`) |
| D1 EU database | `xpo-load-studio-db` (UUID `e8b2efad-4eef-4263-b2cc-5dfc636c469e`) |
| Existing GitHub repository connection | `c4fcc3da-b670-4e13-996d-91d3b62d805b` |
| Most recent audited Worker version | `f6e3fc63-1e61-4f33-89eb-81277ed7a769` |

The dashboard's allocated `workers.dev` address is **not a working URL yet**. Both `workers_dev=false` and `preview_urls=false` are required by the deployment config. There is no authorized public production route at this gate.

## 2. Verified evidence — hosted upload

[GitHub Actions run 39596676298](https://github.com/GabrielValverdeBaez/XPO-Operations/actions/runs/39596676298), trigger commit `4deef7b3677895be143dff646afd0bd8d47ee242`:

- Attempt 1 failed on Cloudflare API error `10021`: `binding DB of type d1 failed to generate`. Python tests, dry-run, assets and XPO resource checks had already passed.
- The **same job** was rerun once without changing the token, code or D1. Attempt 2 **SUCCESS** (job `119213768117`).
- Wrangler reported `Uploaded xpo-load-studio`, `Current Version ID: ed97eb4f-e231-40dd-a57e-63220a363da6`, and `No targets deployed for xpo-load-studio`.
- The upload logged these bindings: `DB` -> the dedicated XPO D1, `LOGIN_LIMITER` (5 requests per 60 seconds), and `ASSETS`. It did **not** prove the hosted application's login or persistence.
- Uploading assets and a Worker version is **not** operational acceptance.

[Read-only Cloudflare API audit run 39599178204](https://github.com/GabrielValverdeBaez/XPO-Operations/actions/runs/39599178204), 2026-10-21:
- API query `GET .../versions`: version present, latest ID matches the one above.
- API query `GET .../deployments`: deployment record present. This does **not** imply an enabled public route.
- API query `GET .../secrets`: **`XPO_LOGIN_KEY` not present** when queried.
- Only version/deployment metadata and secret **names** were checked; **no secret values** and **no D1 records** were accessed.

The Cloudflare ChatGPT connector returned an internal tool error during this session, so verification used the purpose-scoped Cloudflare token securely stored in GitHub Actions and read-only Cloudflare API requests. That token is **not** an app login secret.

Previous local integration evidence remains valid for its original commits:
- [Workerd + local D1 full integration, run 39446374542](https://github.com/GabrielValverdeBaez/XPO-Operations/actions/runs/39446374542) PASS.
- [Load Studio checks, run 39446374450](https://github.com/GabrielValverdeBaez/XPO-Operations/actions/runs/39446374450) PASS.
- Artifact `cloudflare-runtime-evidence` ID `12276231995`. Tests cover HTTPS cookies, real rate limiter, protected assets/API, deterministic ES/EN output, exact 26-column TSV, local D1 history/deduplication, revisions, XLSX and private backup, cross-origin controls and restart persistence. **All of this is local runtime evidence, not remote service acceptance.**

### Relevant corrected integration issues

The pinned Python SDK returns `JsDict` instances; the serializer must accept `dict` subclasses or the login rate limiter result is lost. For D1 batches, manually converting wrapped statement lists to JS broke the borrowed proxy lifetime. Production code now leaves statement conversion to the SDK. The login endpoint is fail-closed when its limit binding or login secret is absent. Regression tests and GitHub CI cover these conditions.

## 3. One operator-controlled action still required

With the Worker version uploaded, go to the [XPO Worker dashboard](https://dash.cloudflare.com/0054188c07d3b5fe7cb20fc4f71dc212/workers/services/view/xpo-load-studio/production):

1. Open **Settings > Variables and secrets** and choose **Production**, never Previews Base.
2. Locate **`XPO_LOGIN_KEY`**, already of type **Secret**. Edit/update its value; do not change its exact name or type. Remove any leftover `XPO_LOGIN_KEY1` Text binding if present.
3. Generate a **new** high-entropy password (recommended 48+ random characters, at least 12 distinct characters) using a password manager. Do not reuse the failed value; keep a private copy in the manager.
4. Choose **Deploy** or the dashboard's equivalent to persist the secret. **Do not** put the password in chat, GitHub, code, logs or a plaintext variable.

The already-configured GitHub Actions secret `XPO_CLOUDFLARE_API_TOKEN` is for deployment API authorization only. It is unrelated to `XPO_LOGIN_KEY`, and must not be copied or used as the application password.

If the dashboard still does not offer Add under Production, stop there and capture the current Settings screen; do not re-create the Worker, alter Previews Base, or paste a secret into this conversation. A controlled private secret-configuration route can then be designed.

## 4. Executor continuation after the operator step

1. After replacing the secret value, run the **bounded HTTPS smoke**, not only the read-only audit: the binding type is already confirmed, but the prior runtime returned HTTP 503 and requires functional validation.
2. Inspect Worker versions, D1 binding ID, rate limiter and the deployed config. Keep `workers_dev` and preview URLs off until ready.
3. Agree a single HTTPS entry route with access protection. Enabling `workers.dev` needs a **deliberate corresponding code+CI security-gate change**; dashboard-only toggles would be overwritten by the next Wrangler deploy. Do not enable any endpoint while the key is missing.
4. With the authorized route enabled, test anonymous `/api/history` (401), unauthenticated assets (redirect), secure+HttpOnly login cookie, invalid/repeated login (401/429), cross-origin rejection, logout and absence of secret disclosure.
5. With **synthetic** test loads only, validate parse/render, ES/EN formatting, TSV's 26 columns, saving, history, deduplication and D1 persistence after a separate deployment. Record non-secret HTTP outcomes and D1 confirmation.
6. Check no public preview, no logs/artifacts containing secrets. Remove only specific synthetic test records after evidence is recorded. Do not import real XPO orders unless corporate authorization for Cloudflare data handling is separately confirmed.
7. Produce `T-016-output` with immutable URLs/run/version IDs and acceptance evidence, then consider closing T-016. Do **not** merge PR #4 automatically. T-008 commercial acceptance and T-014 Mac mini/local acceptance remain independent.

## 5. Security and recovery

No XPO real loads, spreadsheets, credentials or corporate attachments belong in public GitHub. No paid Cloudflare plans or data deletion as a debugging shortcut. Workers Builds native Git integration is optional; the existing **GitHub-hosted Actions** workflow already proved a first-version upload and needs no Mac mini or workstation CLI.

The purpose-scoped deploy workflow runs on code changes in `feat/cloudflare-deployment`, not on documentation-only edits, and uses the XPO-only token and account/Worker/D1 assertions. Do not assume green CI or a version ID equals a public, authenticated, production-ready service.

On future failures, inspect the actual job and binding before changing any permission. The transient `10021` recovered on exactly one identical rerun; this does not guarantee all future failures will be transient.

No task is running autonomously between ChatGPT conversations. Project Route Markdown/YAML is canonical; GitHub Actions is an execution adapter.
