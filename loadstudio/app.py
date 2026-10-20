"""Loopback-first API: no network calls, no raw FOTE logging, no generative AI."""
from datetime import datetime
import io
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import tempfile
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict
from .models import ParseRequest, RenderRequest, Rules, CorridorRate
from .engine import render, HEADERS, CATALOG
from .ingest import parse, workbook_preview, import_rows, FIELD_MAP, IMPORT_FIELDS
from .store import Store

ROOT=Path(__file__).resolve().parents[1]
MAX_BODY=5_500_000
class MappingRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    rows: list[list] = Field(max_length=50)
    mapping: dict[str,int]
class RulesRequest(BaseModel):
    rules: Rules
    expected_revision: int
class RollbackRequest(BaseModel):
    revision: int
    expected_revision: int

def create_app(data_dir=None,testing=False):
    data=Path(data_dir or os.environ.get('XPO_DATA_DIR',Path.home()/'.local/share/xpo-load-studio'))
    store=Store(data/'studio.sqlite3'); token_path=data/'session.token'
    if not token_path.exists():
        fd=os.open(token_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w') as f:f.write(secrets.token_urlsafe(32))
    token=token_path.read_text().strip()
    if len(token)<32:raise RuntimeError('Token local invalido')
    os.chmod(token_path,0o600)
    app=FastAPI(title='XPO Load Studio',docs_url=None,redoc_url=None,openapi_url=None)
    app.state.store=store;app.state.token=token
    hosts={'127.0.0.1','localhost','::1'}
    hosts.update(filter(None,os.environ.get('XPO_ALLOWED_HOSTS','').split(',')))
    if testing:hosts.add('testserver')
    @app.middleware('http')
    async def private_only(request:Request,call_next):
        if request.url.hostname not in hosts:
            return JSONResponse({'detail':'Host no autorizado'},status_code=403)
        origin=request.headers.get('origin')
        if origin and origin not in {f'http://{request.headers.get("host")}',f'https://{request.headers.get("host")}'}:
            return JSONResponse({'detail':'Origen no autorizado'},status_code=403)
        if request.url.path.startswith('/api/') and request.url.path!='/api/health':
            if not secrets.compare_digest(request.headers.get('X-XPO-Token',''),token):
                return JSONResponse({'detail':'Abrir la URL local con su token de sesion'},status_code=401)
        if request.method in ('POST','PUT','DELETE'):
            try:length=int(request.headers.get('content-length','0'))
            except ValueError:return JSONResponse({'detail':'Longitud invalida'},status_code=400)
            if length>MAX_BODY:return JSONResponse({'detail':'Archivo demasiado grande'},status_code=413)
            # Streaming limit also covers clients that omit Content-Length.
            parts=[];total=0
            async for chunk in request.stream():
                total+=len(chunk)
                if total>MAX_BODY:return JSONResponse({'detail':'Archivo demasiado grande'},status_code=413)
                parts.append(chunk)
            request._body=b''.join(parts)
        response=await call_next(request)
        response.headers['Cache-Control']='no-store'
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['X-Frame-Options']='DENY'
        response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
        return response
    @app.exception_handler(ValueError)
    async def invalid(request,exc):return JSONResponse({'detail':str(exc)[:500]},status_code=422)
    @app.get('/')
    def index():return FileResponse(ROOT/'static/index.html')
    @app.get('/api/health')
    def health():return {'status':'ok','version':'0.1.0','mode':'local-no-generative-ai'}
    @app.get('/api/config')
    def config():return {'headers':HEADERS,'catalogs':CATALOG,'mapping_defaults':FIELD_MAP,'import_fields':sorted(IMPORT_FIELDS),'rules':store.rules().model_dump(),'ocr_available':bool(shutil.which('tesseract')),'template_validated_rows':38}
    @app.post('/api/parse')
    def parse_input(req:ParseRequest):return {'drafts':parse(req.text,req.mode)}
    @app.post('/api/render')
    def output(req:RenderRequest):return render(req.load,store.rules(),store.rates(),req.reviewed)
    @app.post('/api/save')
    def save(req:RenderRequest):return store.save(render(req.load,store.rules(),store.rates(),req.reviewed))
    @app.get('/api/history')
    def history():return store.history()
    @app.get('/api/history/{ident}')
    def item(ident:int):return store.get(ident)
    @app.get('/api/rules')
    def rules():return store.rule_history()
    @app.put('/api/rules')
    def rules_update(req:RulesRequest):return store.update_rules(req.rules,req.expected_revision).model_dump()
    @app.post('/api/rules/restore')
    def rules_restore(req:RollbackRequest):return store.restore_rules(req.revision,req.expected_revision).model_dump()
    @app.get('/api/rates')
    def rates():return [x.model_dump(mode='json') for x in store.rates()]
    @app.put('/api/rates')
    def rates_update(req:CorridorRate):store.set_rate(req);return {'saved':req.id}
    @app.post('/api/backup')
    def backup():
        name='studio-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+secrets.token_hex(3)+'.sqlite3'
        folder=data/'backups';folder.mkdir(exist_ok=True,mode=0o700)
        p=store.backup(folder/name)
        return {'filename':p.name,'message':'Copia guardada localmente en el directorio privado de datos'}
    @app.post('/api/excel/preview')
    async def excel(file:UploadFile=File(...)):
        raw=await file.read(MAX_BODY+1)
        try:return {'sheets':workbook_preview(raw)}
        except Exception as e:
            if isinstance(e,ValueError):raise
            raise ValueError('No se pudo leer el XLSX: protegido o corrupto') from e
    @app.post('/api/excel/import')
    def mapped(req:MappingRequest):return {'drafts':import_rows(req.rows,req.mapping)}
    @app.post('/api/ocr')
    async def ocr(file:UploadFile=File(...)):
        command=shutil.which('tesseract')
        if not command:raise HTTPException(503,'OCR opcional no instalado: instalar Tesseract localmente')
        raw=await file.read(MAX_BODY+1)
        if len(raw)>5_000_000:raise ValueError('Imagen demasiado grande')
        from PIL import Image
        try:
            with Image.open(io.BytesIO(raw)) as image:
                if image.format not in ('PNG','JPEG','WEBP') or image.width*image.height>12_000_000:
                    raise ValueError('Imagen no soportada o demasiado grande')
                image.load()
                with tempfile.TemporaryDirectory() as temp:
                    p=Path(temp)/'input.png';image.convert('RGB').save(p)
                    result=subprocess.run([command,str(p),'stdout','--psm','6','tsv'],capture_output=True,text=True,timeout=20,check=True)
        except (OSError,subprocess.SubprocessError) as e:raise ValueError('OCR local fallido: usar texto o formulario') from e
        import csv
        tokens=list(csv.DictReader(io.StringIO(result.stdout),delimiter='\t'));lines={};conf=[]
        for t in tokens:
            if not t.get('text','').strip():continue
            key=(t['block_num'],t['par_num'],t['line_num']);lines.setdefault(key,[]).append(t['text']);conf.append(float(t['conf']))
        text='\n'.join(' '.join(words) for words in lines.values())
        return {'text':text,'mean_word_confidence':sum(conf)/len(conf) if conf else 0,
                'review_required':True,'warning':'Confianza OCR por palabra, no probabilidad de una carga correcta. Revisar todos los campos.'}
    app.mount('/static',StaticFiles(directory=ROOT/'static'),name='static')
    return app
