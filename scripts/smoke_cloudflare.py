"""Actual Python Worker, full auth and persistent local D1; synthetic data only."""
from pathlib import Path
import io
import json
import os
import secrets
import signal
import subprocess
import tempfile
import time
import httpx
from openpyxl import Workbook

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / 'dist/cloudflare'
BASE = 'https://127.0.0.1:8790'
SAMPLE = '''Referencia: CLOUD-SYNTHETIC
Cliente: XPO TRANSPORT SOLUTIONS SPAIN SL
Origen: ES 28909 Getafe
Destino: PT 2675-076 Odivelas
Recogida: 20/10/2026 10:00-16:00
Descarga: 21/10/2026 12:00-13:00
Servicio: FTL
Peso: 15 t
Mercancia: Aceite / Oil
Precio cliente: 900'''


def stop(proc):
    if proc is None or proc.poll() is not None:
        return
    if os.name == 'posix':
        os.killpg(proc.pid, signal.SIGTERM)
    else:
        proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        if os.name == 'posix':
            os.killpg(proc.pid, signal.SIGKILL)
        else:
            proc.kill()
        proc.wait(timeout=10)


def wait_ready(client, proc):
    deadline = time.monotonic() + 150
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError('Worker process exited before readiness')
        try:
            response = client.get('/login', timeout=30)
            if response.status_code == 200:
                return
            raise RuntimeError(f'Login startup status {response.status_code}')
        except httpx.HTTPError:
            time.sleep(1)
    raise RuntimeError('Worker did not serve login within readiness deadline')


def main():
    if any(os.environ.get(name) for name in ('CLOUDFLARE_API_TOKEN', 'CLOUDFLARE_API_KEY')):
        raise SystemExit('Local smoke refuses Cloudflare account credentials')
    config = json.loads((BUNDLE / 'wrangler.jsonc').read_text())
    if not any(item.get('name') == 'LOGIN_LIMITER' for item in config.get('ratelimits', [])):
        raise SystemExit('Full integration requires the production login rate limiter')
    dev = BUNDLE / '.dev.vars'
    if dev.exists():
        raise SystemExit('Refuse to overwrite existing .dev.vars')
    secret = secrets.token_urlsafe(48)
    fd = os.open(dev, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as handle:
        handle.write('XPO_LOGIN_KEY="' + secret + '"\n')
    evidence = {
        'status': 'FAIL', 'runtime': 'actual workerd Python Worker + local D1',
        'production_deployment': False, 'synthetic_data_only': True,
        'rate_limit_binding_tested': False, 'restart_persistence_verified': False,
        'checks': [], 'phase': 'startup',
    }
    checks = evidence['checks']
    proc = None
    try:
        with tempfile.TemporaryDirectory(prefix='xpo-smoke-') as state, tempfile.TemporaryFile(mode='w+') as log:
            def start():
                return subprocess.Popen(
                    ['uv', 'run', 'pywrangler', 'dev', '--local', '--ip', '127.0.0.1',
                     '--port', '8790', '--local-protocol', 'https', '--persist-to', state],
                    cwd=BUNDLE, stdout=log, stderr=subprocess.STDOUT,
                    start_new_session=(os.name == 'posix'),
                    env={**os.environ, 'CI': 'true', 'WRANGLER_SEND_METRICS': 'false'},
                )
            try:
                proc = start()
                with httpx.Client(base_url=BASE, verify=False, timeout=30, trust_env=False) as client:
                    wait_ready(client, proc)
                    assert client.get('/api/history').status_code == 401
                    assert client.get('/static/app.js').status_code == 303
                    checks.append('unauthenticated API and assets protected')
                    evidence['phase'] = 'login'
                    response = client.post('/auth/login', json={'password': secret}, headers={'Origin': BASE})
                    assert response.status_code == 200, response.text
                    assert 'HttpOnly' in response.headers['set-cookie'] and 'Secure' in response.headers['set-cookie']
                    assert client.get('/').status_code == 200
                    assert client.get('/static/app.js').status_code == 200
                    checks.append('HTTPS login with real rate limiter and private static assets')

                    def post(path, data):
                        return client.post(path, json=data, headers={'Origin': BASE})

                    evidence['phase'] = 'D1 bootstrap'
                    response = client.get('/api/config')
                    assert response.status_code == 200, response.text
                    assert response.json()['deployment_mode'] == 'cloudflare'
                    checks.append('D1 schema bootstrap and catalog')
                    evidence['phase'] = 'deterministic engine'
                    draft = post('/api/parse', {'text': SAMPLE, 'mode': 'text'})
                    assert draft.status_code == 200, draft.text
                    request = {'load': draft.json()['drafts'][0]['load'], 'reviewed': True}
                    output = post('/api/render', request)
                    assert output.status_code == 200, output.text
                    cells = output.json()['tsv'].split('\t')
                    assert len(cells) == 26 and cells[24] == '' and cells[6] == '2675'
                    assert '**Origen** / *Origin*: 28909' in output.json()['markdown']
                    checks.append('Python engine, ES/EN and exact 26-column TSV')
                    evidence['phase'] = 'save and deduplication'
                    first = post('/api/save', request).json()
                    duplicate = post('/api/save', request).json()
                    assert not first['duplicate'] and duplicate['duplicate'] and first['id'] == duplicate['id']
                    assert client.get('/api/history').json()[0]['reference'] == 'CLOUD-SYNTHETIC'
                    checks.append('D1 save, duplicate suppression and history')
                    evidence['phase'] = 'rule revisions'
                    rule = client.get('/api/rules').json()[0]['rules']
                    rev = rule['revision']
                    rule.update(revision=rev + 1, reason='Synthetic workerd smoke')
                    body = {'rules': rule, 'expected_revision': rev}
                    assert client.put('/api/rules', json=body, headers={'Origin': BASE}).status_code == 200
                    assert client.put('/api/rules', json=body, headers={'Origin': BASE}).status_code == 422
                    assert post('/api/rules/restore', {'revision': 1, 'expected_revision': rev + 1}).status_code == 200
                    checks.append('D1 compare-and-swap, stale revision rejection and restoration')
                    evidence['phase'] = 'XLSX upload and private backup'
                    workbook = Workbook()
                    workbook.active.append(['reference'])
                    workbook.active.append(['CLOUD-SYNTHETIC'])
                    buffer = io.BytesIO()
                    workbook.save(buffer)
                    response = client.post('/api/excel/preview', content=buffer.getvalue(),
                                           headers={'Origin': BASE, 'Content-Type': 'application/octet-stream'})
                    assert response.status_code == 200, response.text
                    checks.append('openpyxl raw-byte upload in Python Worker')
                    backup = post('/api/backup', {}).json()
                    assert backup['download']['tables']['snapshots'] and secret not in json.dumps(backup)
                    assert client.post('/api/save', json=request, headers={'Origin': 'https://attacker.test'}).status_code == 403
                    checks.append('private backup and cross-origin rejection')

                    # Capture the current rule revision before restarting the entire
                    # workerd process, then verify persistent storage, not memory.
                    persisted = post('/api/save', request).json()
                    assert 'id' in persisted, persisted
                    evidence['phase'] = 'process restart and persistence'
                    stop(proc)
                    proc = None
                    proc = start()
                    wait_ready(client, proc)
                    assert client.get('/api/health').status_code == 200
                    history = client.get('/api/history').json()
                    assert any(row['id'] == persisted['id'] for row in history)
                    assert client.get('/api/rules').json()[0]['revision'] == rev + 2
                    saved = client.get('/api/history/' + str(persisted['id'])).json()
                    assert saved['load']['reference'] == 'CLOUD-SYNTHETIC'
                    repeated = post('/api/save', request).json()
                    assert repeated['duplicate'] and repeated['id'] == persisted['id']
                    evidence['restart_persistence_verified'] = True
                    checks.append('full process restart preserves D1, rules, signed session and deduplication')

                    evidence['phase'] = 'rate limiting'
                    outcomes = []
                    for _ in range(10):
                        response = post('/auth/login', {'password': 'deliberately-invalid-smoke-password'})
                        outcomes.append(response.status_code)
                        if response.status_code == 429:
                            break
                    assert 401 in outcomes and outcomes[-1] == 429, outcomes
                    assert post('/auth/login', {'password': secret}).status_code == 429
                    evidence['rate_limit_binding_tested'] = True
                    checks.append('real login rate limiter rejects repeated attempts with 429')
                    assert post('/auth/logout', {}).status_code == 200
                    assert client.get('/api/history').status_code == 401
                    assert client.get('/static/app.js').status_code == 303
                    checks.append('logout removes private API and asset access')
                    evidence.update(status='PASS', phase='complete')
            except Exception as exc:
                evidence['error_type'] = type(exc).__name__
                log.seek(0)
                text = log.read().replace(secret, 'REDACTED')
                print(text[-8000:])
                raise
            finally:
                stop(proc)
                proc = None
    finally:
        stop(proc)
        dev.unlink(missing_ok=True)
        destination = ROOT / 'evidence/cloudflare-runtime.json'
        destination.parent.mkdir(exist_ok=True)
        destination.write_text(json.dumps(evidence, indent=2) + '\n')
        print(json.dumps(evidence, indent=2))


if __name__ == '__main__':
    main()
