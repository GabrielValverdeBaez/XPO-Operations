"""Build an allowlisted Python/asset bundle. Never includes XLS, DBs or secrets."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'dist/cloudflare'


def build():
    if DEST.exists():shutil.rmtree(DEST)
    package=DEST/'loadstudio';package.mkdir(parents=True)
    # Every business-rule module comes from the same tested canonical implementation.
    for name in ('__init__.py','models.py','engine.py','ingest.py','route_features.py'):
        shutil.copyfile(ROOT/'loadstudio'/name,package/name)
    engine=(package/'engine.py').read_text()
    old="ROOT = Path(__file__).resolve().parents[1]\nAUDIT = json.loads((ROOT/'evidence/template-audit.json').read_text(encoding='utf-8'))"
    if engine.count(old)!=1:raise RuntimeError('Engine catalog loader changed: review build adapter')
    (package/'engine.py').write_text(engine.replace(old,'from ._catalog import AUDIT'),encoding='utf-8')
    audit=json.loads((ROOT/'evidence/template-audit.json').read_text())
    # Only headers/catalogs; exclude operator attachments and unnecessary audit metadata.
    subset={key:audit[key] for key in ('headers','catalogs')}
    (package/'_catalog.py').write_text('# Generated from audited catalogs. Do not edit.\nAUDIT = '+repr(subset)+'\n',encoding='utf-8')
    target=DEST/'cloud_adapter';target.mkdir()
    for name in ('__init__.py','api.py','auth.py','d1.py'):
        shutil.copyfile(ROOT/'cloud_adapter'/name,target/name)
    shutil.copyfile(ROOT/'worker.py',DEST/'worker.py')
    shutil.copyfile(ROOT/'pyproject.toml',DEST/'pyproject.toml')
    config=json.loads((ROOT/'wrangler.jsonc').read_text())
    config['main']='worker.py';config['assets']['directory']='public'
    (DEST/'wrangler.jsonc').write_text(json.dumps(config,indent=2)+'\n')
    public=DEST/'public';(public/'static').mkdir(parents=True)
    for name in ('style.css','app.js'):
        shutil.copyfile(ROOT/'static'/name,public/'static'/name)
    js=(public/'static/app.js').read_text()
    patches = [
        ("const token=()=>sessionStorage.getItem('xpo-token')||'';", "const token=()=>sessionStorage.getItem('xpo-token')||'';\nconst cloudMode=true;"),
        ("if(data instanceof FormData)options.body=data;", "if(data instanceof FormData){options.body=data.get('file');options.headers['Content-Type']='application/octet-stream';}"),
        ("action('#backup',async()=>notice((await api('backup',{})).message));", "action('#backup',async()=>{const backup=await api('backup',{});if(backup.download){const url=URL.createObjectURL(new Blob([JSON.stringify(backup.download,null,2)],{type:'application/json'}));const link=document.createElement('a');link.href=url;link.download=backup.filename;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}notice(backup.message);});"),
        ("notice('Motor local listo. Datos reales solo en este equipo.');", "$('#ocr-file').disabled=true;notice('Acceso privado. Los datos se procesan en Cloudflare y el historial se guarda en D1.');"),
    ]
    for before,after in patches:
        if js.count(before)!=1:raise RuntimeError('Frontend changed: review cloud build adaptation')
        js=js.replace(before,after)
    (public/'static/app.js').write_text(js,encoding='utf-8')
    for name in ('login.html','login.js','login.css'):
        shutil.copyfile(ROOT/'cloud_assets'/name,public/name)
    shutil.copyfile(ROOT/'cloud_assets/cloud.js',public/'static/cloud.js')
    page=(ROOT/'static/index.html').read_text()
    page=page.replace('<title>XPO Load Studio</title>','<title>XPO Load Studio</title><meta name="xpo-deployment" content="cloudflare"><script defer src="/static/cloud.js"></script>')
    page=page.replace('LOCAL &middot; SIN IA GENERATIVA','CLOUDFLARE &middot; ACCESO PRIVADO')
    page=page.replace('</header>','<button id="cloud-logout">Cerrar sesi&oacute;n</button></header>')
    page=page.replace('Historial local','Historial privado en Cloudflare')
    page=page.replace('Crear copia de seguridad','Descargar copia JSON')
    page=page.replace('Capturas con OCR local y revisi&oacute;n obligatoria.','El OCR local no est&aacute; disponible en esta versi&oacute;n alojada.')
    page=page.replace('Datos en tu equipo','Datos procesados en Cloudflare; historial guardado en D1')
    (public/'index.html').write_text(page,encoding='utf-8')
    manifest={str(p.relative_to(DEST)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(DEST.rglob('*')) if p.is_file()}
    (DEST/'bundle-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('PASS: isolated Cloudflare bundle, '+str(len(manifest))+' allowlisted files')
    return manifest

if __name__=='__main__':build()
