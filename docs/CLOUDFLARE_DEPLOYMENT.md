# XPO Load Studio - Cloudflare deployment handoff

Updated: 2026-10-21. Status: **INTEGRATION PASS / GITHUB-HOSTED DEPLOY READY; API TOKEN AND REMOTE ACCEPTANCE PENDING**.

## Browser-only deployment path (preferred for the first release)

No Mac mini, SSH access or software installed on the operator workstation is needed. The feature branch contains `.github/workflows/xpo-cloudflare-deploy.yml`. GitHub-hosted Ubuntu runs the checks and the existing Python `pywrangler deploy` script; no code is rebuilt from scratch.

The workflow triggers on relevant pushes to `feat/cloudflare-deployment` (plus an optional manual dispatch where available). Before a **dedicated** repository secret named `XPO_CLOUDFLARE_API_TOKEN` exists, the deployment steps are skipped. It runs tests, a dry-run, verifies the bundle points only to the existing XPO Worker and EU D1, and refuses `workers_dev=true` and preview URLs. It does not run on pull_request events, `main`, or forks. After setting the token, a further commit to this deployment documentation or to a listed source path triggers a release. Merely saving a secret does not trigger a workflow.

Operator actions, entirely via browser:

1. In Cloudflare > My Profile > API Tokens, create an XPO-only deployment token using the Workers Scripts Edit permission scoped to the relevant account; grant any additional specific permission only if required by the actual deploy error. **Never** use the existing Evenio token or a global API key.
2. Open [GitHub Actions repository secrets](https://github.com/GabrielValverdeBaez/XPO-Operations/settings/secrets/actions), choose New repository secret, name it exactly `XPO_CLOUDFLARE_API_TOKEN` and paste the token value **there only**. Do not paste it into chat, documents or a committed file. The account ID already exists in the allowlisted config and action.
3. Once the operator confirms the secret was saved, create a documentation-only commit to this branch (with the controller), to trigger the protected release. Watch the GitHub Actions result. If credential permissions are insufficient, do not broaden them blindly; review the actual 403 and apply least privilege.
4. With a first Worker version available, set `XPO_LOGIN_KEY` through Cloudflare Settings > Production > Variables and secrets as a **Secret** (32+ character random password). Do not store this application password in GitHub.
5. Keep the workers.dev production URL and preview URLs **disabled** during initial publication. Only activate the production domain after the login Secret, binding, anonymous-denial and security checks are ready. Carry out remote acceptance with synthetic data before declaring T-016 DONE.

The cloud dashboard currently shows the Git repository Connect button disabled before the first Worker version exists, so the first release uses GitHub-hosted Actions instead of interactive local Wrangler or Workers Builds. Cloudflare Builds may be linked later if needed. The Python application deliberately denies access when the login secret or login limiter is missing. Passing GitHub-hosted CI is not proof of remote acceptance.


## Scope and authorization

The operator explicitly authorized private Cloudflare hosting of XPO Load Studio without reliance on the Mac mini, reversible technical work, and dedicated XPO resources. Preserve the deterministic engine, local application and commercial acceptance gates. Do not merge PR #4 automatically, change other projects, purchase paid plans, send offers, or upload real operational data or credentials.

## Verified integration

Code commit: `ff61f8d89bbcbb1b9764d2b01c7618abea5c465d`.

- Cloudflare adapter checks: [run 39446374542](https://github.com/GabrielValverdeBaez/XPO-Operations/actions/runs/39446374542), job `118709265212`: SUCCESS.
- Load Studio checks: [run 39446374450](https://github.com/GabrielValverdeBaez/XPO-Operations/actions/runs/39446374450): SUCCESS.
- Runtime evidence artifact: `cloudflare-runtime-evidence`, ID `12276231995`, digest `sha256:f03e4f3d5203d8745cffa4963735c49aa9bf8850d15de4c020b24debf9095a4b`.

The final workflow tests the unmodified production adapter, without temporary diagnostics. It covers HTTPS login and protected assets/API, the real login rate limiter, deterministic ES/EN and 26-column TSV output, D1 schema bootstrap, saving, deduplication, rule revision conflicts/restoration, XLSX preview, private backup, cross-origin rejection and logout. It also stops and restarts the full workerd process and verifies persisted D1 data, rules and deduplication. Only synthetic data is used.

This is actual workerd plus **local D1**, not a hosted application acceptance result. Every later code change needs its own CI result; these links are evidence for the named commit only.

### Root causes corrected

`workers-runtime-sdk` returns dictionary subclasses (`JsDict`). The previous exact-type check wrongly serialized those Python values back through JavaScript and lost fields such as the rate-limiter `success` value. `native()` now respects dict subclasses. The SDK already converts Python lists and unwraps D1 statement wrappers. Manually applying `pyodide.to_js()` created borrowed proxies that expired before the async batch used them; statement lists now go directly through the SDK. Regression tests cover both cases. Removing the login limiter was a temporary diagnostic, not the fix, and is no longer done.

Primary source: [official Workers Python SDK RPC implementation](https://github.com/cloudflare/workers-py/blob/main/packages/runtime-sdk/src/workers/rpc.py).

## Real dedicated resources

Account: `0054188c07d3b5fe7cb20fc4f71dc212`, authenticated as `gabriel.valverde.baez@gmail.com`.

| Resource | Verified identifier and state |
|---|---|
| Worker | `xpo-load-studio`, ID `9f213a235e0f402a99631cc17c4a37af` |
| Worker release | Created, but `deployed_on = null`; no application version uploaded |
| Public routes | workers.dev disabled; preview URLs disabled |
| D1 | `xpo-load-studio-db`, UUID `e8b2efad-4eef-4263-b2cc-5dfc636c469e` |
| D1 location | Jurisdiction `eu`; read replication disabled |
| D1 connection check | Actual API query `SELECT 1 AS connection_ok` returned 200 / success / 1 |
| Repository connection | `c4fcc3da-b670-4e13-996d-91d3b62d805b` |
| GitHub repository | `1426684636`, GabrielValverdeBaez/XPO-Operations |
| Branch / PR | `feat/cloudflare-deployment` / #4, unmerged |

The address assigned by Cloudflare is `https://xpo-load-studio.gabriel-valverde-baez.workers.dev`. **It is disabled and is not evidence of a functional hosted app.** Do not mark the deployment DONE merely because this address or Worker object exists.

Project dashboard: https://dash.cloudflare.com/0054188c07d3b5fe7cb20fc4f71dc212/workers/services/view/xpo-load-studio/production

## Exact remaining access gate

MCP OAuth can read/create Workers, D1 and the repository connection. It cannot create API tokens: the account permission-group endpoint returns HTTP 403 and explicitly states that no OAuth scope covers that endpoint. Reconnecting the same MCP does not supply a non-interactive build credential.

No XPO build token exists. The one pre-existing build token belongs to another project and was not used, changed or copied. A build trigger has therefore **not** been created. No login secret has been set. Never extract connector credentials, copy another project's token, commit a token, or request secrets in chat.

### One Cloudflare dashboard setup session

1. Open the existing `xpo-load-studio` Worker, then its Builds configuration and connect the Git repository above. Select branch `feat/cloudflare-deployment`, root `/`, and disable preview-branch builds. The API-level repository connection already exists; reuse it where offered.
2. Generate/authorize a deployment credential dedicated to XPO using the dashboard's supported token flow. Keep permissions and scope as narrow as supported for this Worker and its existing D1 binding. Do not reuse another project's build token. Keep the free plan; stop if a purchase or paid upgrade is required.
3. Set these commands (the application build/deploy commands are already defined in package.json):

Build command:
```sh
python -m pip install uv==0.13.3 && npm run build
```

Deploy command:
```sh
npm run deploy
```

These are the intended Workers Builds settings; execution on that hosted build image remains unverified. GitHub CI has verified the same allowlisted build and Pywrangler dry-run. If the hosted Python environment disallows pip installation, use a project-local virtual environment; do not modify system packages or other projects.

4. In Worker Settings > Variables and Secrets, create `XPO_LOGIN_KEY` with type **Secret**, using a password manager's high-entropy random password of at least 32 characters. Save it privately; do not put it in GitHub, chat, build logs or plaintext variables. Without a valid secret the app deliberately returns 503 and remains closed.

The credential for deployment and `XPO_LOGIN_KEY` are different secrets with different purposes. The former authorizes CI upload; the latter authenticates app users. No secret values are recorded here.

## Hosted acceptance - still required

After credential setup, inspect the actual build trigger and run, ensure it uses only the named XPO Worker and D1, and deploy this branch. Inspect the produced Worker version and binding IDs. Check the real HTTPS URL without credentials (private API 401, private assets redirect), then valid login (Secure/HttpOnly cookie), invalid/repeated login and cross-origin rejection. Use synthetic data only to verify parsing, rendering, saving, duplicate suppression and reading the same record after a separate Worker version deployment/restart. Confirm remote D1 holds that record, then remove only the explicitly identified synthetic test data. Verify logout, private backup, no public preview route and no credentials in artifacts/logs.

Local restart evidence is not a substitute for remote persistence evidence. Record the actual URL, version, CI build ID, HTTP results and non-secret D1 verification before marking T-016 DONE. Commercial acceptance and local Mac installation remain independent unfinished gates.

## Recovery

Do not recreate the existing Worker, D1 or repository connection. Read their exact IDs before any write. Keep the app closed if an auth or binding check fails. No paid plans or real data imports. Resume from T-016, not from old MCP reconnection instructions. Nothing is running autonomously between conversations.
