"""One local OCR integration check with a synthetic image; not an accuracy benchmark."""
import io
import json
from pathlib import Path
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw, ImageFont
from loadstudio.app import create_app
with tempfile.TemporaryDirectory() as temp:
    app=create_app(temp,testing=True)
    image=Image.new('RGB',(1600,420),'white');draw=ImageDraw.Draw(image)
    try:font=ImageFont.truetype('DejaVuSans.ttf',52)
    except OSError:font=ImageFont.load_default(size=52)
    draw.text((40,60),'REFERENCE: SYN-IMAGE\nWEIGHT: 15000 KG',font=font,fill='black')
    b=io.BytesIO();image.save(b,format='PNG')
    with TestClient(app) as c:
        c.headers['X-XPO-Token']=app.state.token
        r=c.post('/api/ocr',files={'file':('synthetic.png',b.getvalue(),'image/png')})
        if r.status_code==503:
            report={'status':'SKIP','reason':'Optional Tesseract is not installed'}
        else:
            assert r.status_code==200,r.text
            value=r.json();assert '15000' in value['text'] and value['review_required'] is True
            report={'status':'PASS','source':'single synthetic English image','text':value['text'],'confidence':value['mean_word_confidence'],'review_required':True,'not_proven':'accuracy on real FOTE screenshots or Spanish labels'}
        (ROOT/'evidence/ocr-smoke.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
