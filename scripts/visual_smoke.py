"""Offline DOM/visual check with fixture-backed fetch. Not a live-browser E2E test.
No network requests: the API is tested separately with TestClient.
"""
import json
import os
from pathlib import Path
import re
import sys
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from loadstudio.models import Load
from loadstudio.engine import render, CATALOG, HEADERS, DEFAULT_RULES
from loadstudio.ingest import parse, IMPORT_FIELDS, FIELD_MAP
text='''Referencia: DEMO-001
Cliente: XPO TRANSPORT SOLUTIONS SPAIN SL
Origen: ES 28909 Getafe
Destino: PT 2675-076 Odivelas
Recogida: 20/10/2026 10:00-16:00
Descarga: 21/10/2026 12:00-13:00
Servicio: FTL
Peso: 15 t
Mercancia: Aceite / Oil
Precio cliente: 900'''
drafts=parse(text);raw=Load.model_validate(drafts[0]['load'])
fixture={'config':{'catalogs':CATALOG,'headers':HEADERS,'import_fields':sorted(IMPORT_FIELDS),'mapping_defaults':FIELD_MAP},'parse':{'drafts':drafts},'draft':render(raw),'review':render(raw,reviewed=True)}
html=re.sub(r'<link[^>]*>|<script[^>]*>.*?</script>','',(ROOT/'static/index.html').read_text(),flags=re.S)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('XPO_CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1050});errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(html);page.add_style_tag(content=(ROOT/'static/style.css').read_text())
    page.add_script_tag(content="Object.defineProperty(window,'sessionStorage',{value:{getItem:()=>'',setItem:()=>{}}});const fixture="+json.dumps(fixture)+";window.fetch=async(path,opts)=>{let value;if(path.endsWith('config'))value=fixture.config;else if(path.endsWith('parse'))value=fixture.parse;else if(path.endsWith('render'))value=JSON.parse(opts.body).reviewed?fixture.review:fixture.draft;else throw Error('Unexpected mocked path');return new Response(JSON.stringify(value),{status:200,headers:{'Content-Type':'application/json'}});};")
    page.add_script_tag(content=(ROOT/'static/app.js').read_text())
    expect(page.locator('#notice')).to_contain_text('Motor local listo')
    page.click('#sample');page.click('#analyze');expect(page.locator('[data-path="reference"]')).to_have_value('DEMO-001')
    page.click('#preview');expect(page.locator('#copy-tsv')).to_be_disabled()
    page.check('#reviewed');expect(page.locator('#result-status')).to_have_text('REVISADO')
    cells=page.locator('#tsv-output').input_value().split('\t');assert len(cells)==26 and cells[24]==''
    assert '28909' not in page.locator('#rich-output strong').all_text_contents()
    page.locator('#notice').evaluate("el=>el.textContent='Vista de prueba con datos sinteticos. API simulada para revision visual.'")
    page.screenshot(path=str(ROOT/'evidence/ui-desktop.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
    page.screenshot(path=str(ROOT/'evidence/ui-mobile.png'),full_page=True)
    page.locator('[data-path="weight_kg"]').fill('16000');expect(page.locator('#copy-tsv')).to_be_disabled();expect(page.locator('#reviewed')).not_to_be_checked()
    assert not errors,errors
    report={'status':'PASS','mode':'offline DOM with fixture-backed API; not live E2E','browser':browser.version,'checks':['source form','populated fields','review gating','26 cells including trailing empties','format label boundaries','edit invalidation','desktop rendering','390px mobile no overflow','no JS page errors'],'not_tested':['browser-to-localhost blocked by administrator policy','clipboard system integration','actual Mac mini deployment']}
    (ROOT/'evidence/visual-smoke.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));browser.close()
