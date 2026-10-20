"""Run the actual Python Worker + local D1, without any Cloudflare account/token."""
from pathlib import Path
import io
import json
import os
import secrets
import subprocess
import tempfile
import time
import httpx
from openpyxl import Workbook

ROOT=Path(__file__).resolve().parents[1]
BUNDLE=ROOT/'dist/cloudflare'
BASE='https://127.0.0.1:8790'
SAMPLE='''Referencia: CLOUD-SYNTHETIC
Cliente: XPO TRANSPORT SOLUTIONS SPAIN SL
Origen: ES 28909 Getafe
Destino: PT 2675-076 Odivelas
Recogida: 20/10/2026 10:00-16:00
Descarga: 21/10/2026 12:00-13:00
Servicio: FTL
Peso: 15 t
Mercancia: Aceite / Oil
Precio cliente: 900'''


def main():
    dev=BUNDLE/'.dev.vars'
    if dev.exists():raise SystemExit('Refuse to overwrite existing .dev.vars')
    secret=secrets.token_urlsafe(48)
    dev.write_text('XPO_LOGIN_KEY="'+secret+'"\n');dev.chmod(0o600)
    checks=[];proc=None
    try:
        with tempfile.TemporaryFile(mode='w+') as log:
            proc=subprocess.Popen(['uv','run','pywrangler','dev','--ip','127.0.0.1','--port','8790','--local-protocol','https'],cwd=BUNDLE,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CI':'true','WRANGLER_SEND_METRICS':'false'})
            try:
                with httpx.Client(base_url=BASE,verify=False,timeout=10,trust_env=False) as c:
                    ready=False
                    deadline=time.monotonic()+150
                    failed_responses=0
                    while time.monotonic()<deadline:
                        if proc.poll() is not None:raise RuntimeError('Worker process exited')
                        try:
                            r=c.get('/login',timeout=2)
                            if r.status_code==200:ready=True;break
                            failed_responses+=1
                            if failed_responses>=3:
                                raise RuntimeError(f"Login startup returned {r.status_code}: {r.text[:300]}")
                        except httpx.HTTPError:pass
                        time.sleep(1)
                    if not ready:raise RuntimeError('Worker did not serve login')
                    assert c.get('/api/history').status_code==401
                    assert c.get('/static/app.js').status_code==303
                    checks.append('unauthenticated API and assets protected')
                    r=c.post('/auth/login',json={'password':secret},headers={'Origin':BASE})
                    assert r.status_code==200,r.text
                    assert 'HttpOnly' in r.headers['set-cookie'] and 'Secure' in r.headers['set-cookie']
                    assert c.get('/').status_code==200
                    assert c.get('/static/app.js').status_code==200
                    checks.append('HTTPS login, signed cookie and private static assets')
                    config=c.get('/api/config')
                    assert config.status_code==200,config.text
                    assert config.json()['deployment_mode']=='cloudflare'
                    checks.append('D1 schema bootstrap and catalog')
                    def post(path,data):return c.post(path,json=data,headers={'Origin':BASE})
                    draft=post('/api/parse',{'text':SAMPLE,'mode':'text'})
                    assert draft.status_code==200,draft.text
                    request={'load':draft.json()['drafts'][0]['load'],'reviewed':True}
                    output=post('/api/render',request)
                    assert output.status_code==200,output.text
                    cells=output.json()['tsv'].split('\t')
                    assert len(cells)==26 and cells[24]=='' and cells[6]=='2675'
                    assert '**Origen** / *Origin*: 28909' in output.json()['markdown']
                    assert '950' not in output.json()['market_basis'].__str__()
                    checks.append('Python engine, ES/EN and exact 26-column TSV')
                    first=post('/api/save',request).json();duplicate=post('/api/save',request).json()
                    assert not first['duplicate'] and duplicate['duplicate'] and first['id']==duplicate['id']
                    assert c.get('/api/history').json()[0]['reference']=='CLOUD-SYNTHETIC'
                    checks.append('D1 save, duplicate suppression and history')
                    rule=c.get('/api/rules').json()[0]['rules'];rev=rule['revision'];rule.update(revision=rev+1,reason='Synthetic workerd smoke')
                    body={'rules':rule,'expected_revision':rev}
                    assert c.put('/api/rules',json=body,headers={'Origin':BASE}).status_code==200
                    assert c.put('/api/rules',json=body,headers={'Origin':BASE}).status_code==422
                    assert post('/api/rules/restore',{'revision':1,'expected_revision':rev+1}).status_code==200
                    checks.append('D1 compare-and-swap, revision conflict and restoration')
                    w=Workbook();w.active.append(['reference']);w.active.append(['CLOUD-SYNTHETIC']);b=io.BytesIO();w.save(b)
                    r=c.post('/api/excel/preview',content=b.getvalue(),headers={'Origin':BASE,'Content-Type':'application/octet-stream'})
                    assert r.status_code==200,r.text
                    checks.append('openpyxl raw-byte upload in Python Worker')
                    backup=post('/api/backup',{}).json()
                    assert backup['download']['tables']['snapshots'] and secret not in json.dumps(backup)
                    assert c.post('/api/save',json=request,headers={'Origin':'https://attacker.test'}).status_code==403
                    assert post('/auth/logout',{}).status_code==200
                    assert c.get('/api/history').status_code==401
                    checks.append('private backup, cross-origin rejection, logout')
                result={'status':'PASS','runtime':'actual workerd Python Worker + local D1','production_deployment':False,'synthetic_data_only':True,'checks':checks}
                (ROOT/'evidence/cloudflare-runtime.json').write_text(json.dumps(result,indent=2)+'\n')
                print(json.dumps(result,indent=2))
            except Exception:
                log.seek(0);text=log.read().replace(secret,'REDACTED')
                print(text[-14000:])
                raise
    finally:
        if proc is not None:
            proc.terminate()
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()
        dev.unlink(missing_ok=True)

if __name__=='__main__':main()
