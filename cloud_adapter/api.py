"""Authenticated Cloudflare API sharing the tested deterministic Python engine."""
import hashlib
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ConfigDict
from loadstudio.models import ParseRequest, RenderRequest, Rules, CorridorRate
from loadstudio.engine import render, HEADERS, CATALOG
from loadstudio.ingest import parse, workbook_preview, import_rows, FIELD_MAP, IMPORT_FIELDS
from .auth import COOKIE, TTL, key_valid, password_matches, issue_session, valid_session
from .d1 import D1Store, native

MAX_BODY = 5_500_000
SECURITY = {
    'Cache-Control':'no-store', 'X-Content-Type-Options':'nosniff', 'X-Frame-Options':'DENY',
    'Referrer-Policy':'no-referrer', 'X-Robots-Tag':'noindex, nofollow',
    'Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
}

class LoginRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    password: str = Field(min_length=1,max_length=512)

class MappingRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    rows: list[list] = Field(max_length=50)
    mapping: dict[str,int]

class RulesRequest(BaseModel):
    rules: Rules
    expected_revision: int

class RollbackRequest(BaseModel):
    revision: int
    expected_revision: int


def create_cloud_app(test_env=None):
    app = FastAPI(title='XPO Load Studio Cloudflare',docs_url=None,redoc_url=None,openapi_url=None)

    @app.middleware('http')
    async def protected(request, call_next):
        env = request.scope.get('env', test_env)
        key = getattr(env,'XPO_LOGIN_KEY',None)
        async def dispatch():
            if request.url.scheme != 'https' and request.url.hostname not in ('localhost','127.0.0.1'):
                return JSONResponse({'detail':'HTTPS obligatorio'},status_code=400)
            if not key_valid(key):
                return JSONResponse({'detail':'Acceso cerrado. Configurar XPO_LOGIN_KEY como Secret en Cloudflare (clave aleatoria de 32 o mas caracteres).'},status_code=503)
            origin = request.headers.get('origin')
            own = str(request.base_url).rstrip('/')
            if origin and origin != own:
                return JSONResponse({'detail':'Origen no autorizado'},status_code=403)
            if request.headers.get('sec-fetch-site') == 'cross-site':
                return JSONResponse({'detail':'Solicitud entre sitios no autorizada'},status_code=403)
            if request.method not in ('GET','HEAD'):
                # Browser writes require an explicit same-origin Origin, including login/logout.
                if origin != own:
                    return JSONResponse({'detail':'Origen de escritura requerido'},status_code=403)
                try:
                    size = int(request.headers.get('content-length','0'))
                except ValueError:
                    return JSONResponse({'detail':'Longitud invalida'},status_code=400)
                if size < 0 or size > MAX_BODY:
                    return JSONResponse({'detail':'Entrada demasiado grande'},status_code=413)
                total, parts = 0, []
                async for chunk in request.stream():
                    total += len(chunk)
                    if total > MAX_BODY:
                        return JSONResponse({'detail':'Entrada demasiado grande'},status_code=413)
                    parts.append(chunk)
                request._body = b''.join(parts)
            public = request.url.path in ('/login','/login.js','/login.css','/auth/login')
            if not public and not valid_session(request.cookies.get(COOKIE,''),key):
                if request.url.path.startswith(('/api/','/auth/')):
                    return JSONResponse({'detail':'Sesion caducada. Vuelve a iniciar sesion sin cerrar esta pestana.', 'login_url':'/login'},status_code=401)
                return RedirectResponse('/login',status_code=303)
            request.state.env = env
            request.state.login_key = key
            if request.url.path.startswith('/api/') and request.url.path != '/api/health':
                if not getattr(env,'DB',None):
                    return JSONResponse({'detail':'Falta el binding D1 DB'},status_code=503)
                try:
                    request.state.store = await D1Store(env.DB).ensure()
                except Exception:
                    # Provider errors can include bound parameters: never echo them to clients/logs.
                    return JSONResponse({'detail':'No se puede abrir el almacen D1. Revisar la configuracion.'},status_code=503)
            return await call_next(request)
        response = await dispatch()
        for name,value in SECURITY.items(): response.headers[name]=value
        if request.url.scheme == 'https':response.headers['Strict-Transport-Security']='max-age=31536000'
        return response

    @app.exception_handler(RequestValidationError)
    async def bad_shape(request,exc):
        return JSONResponse({'detail':[{'loc':list(e['loc']),'msg':e['msg']} for e in exc.errors()]},status_code=422)

    @app.exception_handler(ValueError)
    async def invalid(request,exc):
        return JSONResponse({'detail':str(exc)[:500]},status_code=422)

    @app.post('/auth/login')
    async def login(payload:LoginRequest,request:Request):
        limiter = getattr(request.state.env,'LOGIN_LIMITER',None)
        if limiter is None:
            return JSONResponse({'detail':'Acceso cerrado: falta el limitador de intentos LOGIN_LIMITER.'},status_code=503)
        from .d1 import native
        # Cloudflare supplies this IP header. It is hashed and never persisted by the app.
        key = hashlib.sha256(request.headers.get('cf-connecting-ip','unknown').encode()).hexdigest()
        try:
            from pyodide.ffi import to_js
            from js import Object
            args = to_js({'key':key},dict_converter=Object.fromEntries)
        except ImportError:
            args = {'key':key}
        allowed = native(await limiter.limit(args))
        if not allowed.get('success'):
            return JSONResponse({'detail':'Demasiados intentos. Vuelve a intentarlo en un minuto.'},status_code=429)
        if not password_matches(payload.password,request.state.login_key):
            return JSONResponse({'detail':'Clave incorrecta'},status_code=401)
        response = JSONResponse({'ok':True})
        response.set_cookie(COOKIE,issue_session(request.state.login_key),max_age=TTL,secure=True,httponly=True,samesite='strict',path='/')
        return response

    @app.post('/auth/logout')
    async def logout():
        response=JSONResponse({'ok':True})
        response.delete_cookie(COOKIE,path='/',secure=True,httponly=True,samesite='strict')
        return response

    @app.get('/api/health')
    async def health(): return {'status':'ok','version':'0.2.0-cloud','mode':'cloudflare-no-generative-ai'}

    @app.get('/api/config')
    async def config(request:Request):
        return {'headers':HEADERS,'catalogs':CATALOG,'mapping_defaults':FIELD_MAP,'import_fields':sorted(IMPORT_FIELDS),
                'rules':(await request.state.store.rules()).model_dump(),'ocr_available':False,'template_validated_rows':38,'deployment_mode':'cloudflare'}

    @app.post('/api/parse')
    async def parse_input(req:ParseRequest):return {'drafts':parse(req.text,req.mode)}

    async def prepare(req,store):
        return render(req.load,await store.rules(),await store.rates(),req.reviewed)

    @app.post('/api/render')
    async def output(req:RenderRequest,request:Request):return await prepare(req,request.state.store)

    @app.post('/api/save')
    async def save(req:RenderRequest,request:Request):return await request.state.store.save(await prepare(req,request.state.store))

    @app.get('/api/history')
    async def history(request:Request):return await request.state.store.history()

    @app.get('/api/history/{ident}')
    async def item(ident:int,request:Request):return await request.state.store.get(ident)

    @app.get('/api/rules')
    async def rules(request:Request):return await request.state.store.rule_history()

    @app.put('/api/rules')
    async def rules_update(req:RulesRequest,request:Request):return (await request.state.store.update_rules(req.rules,req.expected_revision)).model_dump()

    @app.post('/api/rules/restore')
    async def restore(req:RollbackRequest,request:Request):return (await request.state.store.restore_rules(req.revision,req.expected_revision)).model_dump()

    @app.get('/api/rates')
    async def rates(request:Request):return [x.model_dump(mode='json') for x in await request.state.store.rates()]

    @app.put('/api/rates')
    async def rates_update(req:CorridorRate,request:Request):
        await request.state.store.set_rate(req)
        return {'saved':req.id}

    @app.post('/api/backup')
    async def backup(request:Request):
        return {'download':await request.state.store.backup(),'filename':'xpo-cloud-backup.json','message':'Copia JSON descargada. Guardala en un lugar privado.'}

    @app.post('/api/excel/preview')
    async def excel(request:Request):
        # Cloud UI uploads raw bytes; no tempfile/thread/subprocess dependency in Workers.
        if request.headers.get('content-type')!='application/octet-stream':
            return JSONResponse({'detail':'Enviar el XLSX como bytes'},status_code=415)
        try:return {'sheets':workbook_preview(await request.body())}
        except ValueError:raise
        except Exception as exc:raise ValueError('No se pudo leer el XLSX') from exc

    @app.post('/api/excel/import')
    async def mapped(req:MappingRequest):return {'drafts':import_rows(req.rows,req.mapping)}

    @app.post('/api/ocr')
    async def ocr():return JSONResponse({'detail':'OCR Tesseract no disponible en Cloudflare. Usar FOTE, texto o XLSX.'},status_code=503)

    @app.get('/{path:path}')
    async def frontend(path:str,request:Request):
        if path.startswith(('api/','auth/')):return JSONResponse({'detail':'Ruta inexistente'},status_code=404)
        asset_path = 'login.html' if path=='login' else path or 'index.html'
        allowed = {'index.html','login.html','login.js','login.css','static/app.js','static/style.css','static/cloud.js'}
        # /login.html cannot bypass auth; only /login is public.
        if asset_path not in allowed:return Response('Not found',status_code=404)
        resp=await request.state.env.ASSETS.fetch('https://assets.invalid/'+asset_path)
        data=await resp.bytes()
        if hasattr(data,'to_py'):data=data.to_py()
        content_type=resp.headers.get('content-type') or 'application/octet-stream'
        return Response(bytes(data),status_code=resp.status,media_type=content_type)

    return app

app=create_cloud_app()
