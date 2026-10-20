"""Optional browser smoke test, using a real loopback server and a temporary DB.
Run with XPO_CHROMIUM=/path/to/chromium python scripts/smoke_browser.py.
The supplied URL token is never written to the report or screenshot.
"""
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import urllib.request
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[1]

def main():
    with tempfile.TemporaryDirectory() as temp:
        env={**os.environ,'XPO_DATA_DIR':temp,'PYTHONPATH':str(ROOT)}
        code="import uvicorn; from loadstudio.app import create_app; uvicorn.run(create_app(),host='127.0.0.1',port=8779,access_log=False,log_level='error')"
        process=subprocess.Popen([sys.executable,'-c',code],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        try:
            for _ in range(100):
                if process.poll() is not None:raise RuntimeError(process.stderr.read().decode())
                try:
                    urllib.request.urlopen('http://127.0.0.1:8779/api/health',timeout=.5).close();break
                except OSError:time.sleep(.1)
            else:raise RuntimeError('Server failed to start')
            token=(Path(temp)/'session.token').read_text()
            with sync_playwright() as p:
                executable=os.environ.get('XPO_CHROMIUM')
                kwargs={'executable_path':executable} if executable else {}
                browser=p.chromium.launch(headless=True,args=['--no-sandbox'],**kwargs)
                context=browser.new_context(viewport={'width':1440,'height':1050},permissions=['clipboard-read','clipboard-write'])
                page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                page.goto('http://127.0.0.1:8779/#token='+token)
                expect(page.locator('#notice')).to_contain_text('Motor local listo')
                page.click('#sample');page.click('#analyze')
                expect(page.locator('[data-path="reference"]')).to_have_value('DEMO-001')
                expect(page.locator('[data-path="destination.postcode"]')).to_have_value('2675-076')
                page.click('#preview');expect(page.locator('#result-status')).to_have_text('BORRADOR')
                expect(page.locator('#copy-tsv')).to_be_disabled()
                page.check('#reviewed');expect(page.locator('#result-status')).to_have_text('REVISADO')
                tsv=page.locator('#tsv-output').input_value();cells=tsv.split('\t')
                assert len(cells)==26 and cells[24]=='' and cells[6]=='2675'
                assert '2675-076' in page.locator('#rich-output').inner_text()
                bolds=page.locator('#rich-output strong').all_text_contents()
                assert not any(x in ['28909','2675-076','900,00 \u20ac'] for x in bolds)
                page.click('#copy-tsv');expect(page.locator('#notice')).to_contain_text('Copiado');assert page.evaluate('navigator.clipboard.readText()')==tsv
                page.click('#save');expect(page.locator('#notice')).to_contain_text('Guardado')
                page.click('#save');expect(page.locator('#notice')).to_contain_text('no se ha duplicado')
                page.locator('[data-path="weight_kg"]').fill('16000');expect(page.locator('#copy-tsv')).to_be_disabled()
                expect(page.locator('#reviewed')).not_to_be_checked()
                page.click('[data-tab="history"]');expect(page.locator('.history-row')).to_have_count(1)
                page.click('.history-row button');expect(page.locator('[data-path="weight_kg"]')).to_have_value('15000')
                expect(page.locator('#copy-tsv')).to_be_disabled()
                page.click('[data-tab="rules"]');expect(page.locator('#rules-json')).to_contain_text('')
                expect(page.locator('#rules-json')).to_have_value(re.compile(r'"revision"'))
                rules=json.loads(page.locator('#rules-json').input_value());rules['reason']='Browser smoke test'
                page.locator('#rules-json').fill(json.dumps(rules));page.click('#save-rules')
                expect(page.locator('#notice')).to_contain_text('nueva revision')
                page.click('[data-tab="prepare"]');page.check('#reviewed');expect(page.locator('#result-status')).to_have_text('REVISADO')
                page.locator('.results').scroll_into_view_if_needed()
                page.screenshot(path=str(ROOT/'evidence/ui-desktop.png'),full_page=True)
                page.set_viewport_size({'width':390,'height':844})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                page.screenshot(path=str(ROOT/'evidence/ui-mobile.png'),full_page=True)
                assert not errors,errors
                report={'status':'PASS','browser':browser.version,'checks':['server startup','token session','free text import','manual draft review','26 TSV cells','Y empty','PT postcode conversion','bold label boundary','clipboard trailing tabs','save and duplicate detection','edit invalidates review','history reopens draft','rule version update','mobile overflow','no JavaScript page errors'],'synthetic_data_only':True}
                (ROOT/'evidence/browser-smoke.json').write_text(json.dumps(report,indent=2)+'\n')
                print(json.dumps(report,indent=2));browser.close()
        finally:
            process.terminate()
            try:process.wait(timeout=5)
            except subprocess.TimeoutExpired:process.kill();process.wait()
if __name__=='__main__':main()
