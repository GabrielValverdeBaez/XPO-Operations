"""Read-only BIFF8 audit. No macros/formulas are executed; no third-party packages.

Deliberately bounded: CFB v3/v4 normal Workbook stream, BIFF8 with unsegmented
SST, scalar cells, name/3D area tokens, list and numeric DV formulas. Rejects
unsupported structures rather than returning a partial 'verified' result.
Microsoft MS-XLS 2.4.95, MS-CFB. Intended for the supplied blank template.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path

class Unsupported(ValueError):
    pass

def u16(b, p=0): return struct.unpack_from('<H', b, p)[0]
def u32(b, p=0): return struct.unpack_from('<I', b, p)[0]

def workbook_stream(b: bytes) -> bytes:
    if len(b) > 8_000_000 or b[:8] != bytes.fromhex('d0cf11e0a1b11ae1'):
        raise Unsupported('Not a bounded CFB XLS file')
    size = 1 << u16(b, 30)
    if size not in (512, 4096) or u32(b, 72):
        raise Unsupported('Unsupported sector size or extended DIFAT')
    def sector(sid):
        start = (sid + 1) * size
        if sid >= 0xfffffffa or start + size > len(b):
            raise Unsupported('Sector out of bounds')
        return b[start:start+size]
    fat = []
    for p in range(76, 512, 4):
        sid = u32(b, p)
        if sid < 0xfffffffa:
            fat.extend(struct.unpack('<'+'I'*(size//4), sector(sid)))
    def chain(sid):
        seen, out = set(), []
        while sid < 0xfffffffa:
            if sid in seen or sid >= len(fat):
                raise Unsupported('Cyclic/invalid FAT')
            seen.add(sid); out.append(sector(sid)); sid = fat[sid]
        return b''.join(out)
    directory = chain(u32(b, 48))
    for p in range(0, len(directory), 128):
        e = directory[p:p+128]
        if len(e) != 128: raise Unsupported('Truncated directory')
        n = u16(e, 64)
        if n < 2: continue
        if n > 64: raise Unsupported('Invalid directory name')
        name = e[:n-2].decode('utf-16le')
        if name in ('Workbook', 'Book'):
            length = struct.unpack_from('<Q', e, 120)[0]
            if length < u32(b, 56): raise Unsupported('Mini Workbook not supported')
            stream = chain(u32(e, 116))
            if length > len(stream): raise Unsupported('Truncated Workbook')
            return stream[:length]
    raise Unsupported('Workbook stream not found')

def records(w):
    p = 0
    while p + 4 <= len(w):
        op, n = struct.unpack_from('<HH', w, p)
        if not op and not n: return
        if p+4+n > len(w): raise Unsupported('Truncated BIFF record')
        yield op, w[p+4:p+4+n], p
        p += n+4

def string(b, p=0, short=False, rich=False):
    n = b[p] if short else u16(b, p)
    p += 1 if short else 2
    flags = b[p]; p += 1
    nr = u16(b, p) if rich and flags & 8 else 0
    if rich and flags & 8: p += 2
    ext = u32(b, p) if rich and flags & 4 else 0
    if rich and flags & 4: p += 4
    size = n*(2 if flags & 1 else 1)
    if p+size+nr*4+ext > len(b): raise Unsupported('Truncated unicode string')
    text = b[p:p+size].decode('utf-16le' if flags & 1 else 'latin1')
    return text, p+size+nr*4+ext

def rk(n):
    val = ((n if n < 0x80000000 else n-0x100000000) >> 2) if n & 2 else struct.unpack('<d', struct.pack('<II', 0, n & ~3))[0]
    return val/100 if n & 1 else val

def cellname(row, col):
    s = ''; col += 1
    while col:
        col, r = divmod(col-1, 26); s = chr(65+r)+s
    return s+str(row+1)

def formula(b, names, externals, sheets):
    if not b: return None
    if b[0] == 0x23 and len(b) == 5:
        return {'name': names[u32(b, 1)-1]['name']}
    if b[0] == 0x1e and len(b) == 3: return u16(b, 1)
    if b[0] == 0x1f and len(b) == 9: return struct.unpack_from('<d', b, 1)[0]
    if b[0] in (0x3b, 0x5b, 0x7b) and len(b) == 11:
        ext, r1, r2, c1, c2 = struct.unpack_from('<HHHHH', b, 1)
        entry = externals[ext]
        if entry[1] != entry[2]: raise Unsupported('Multi-sheet area')
        return {'sheet': sheets[entry[1]], 'range': [r1, r2, c1 & 0x3fff, c2 & 0x3fff]}
    if b[0] == 0x17:
        text, end = string(b, 1, short=True)
        if end == len(b): return text
    raise Unsupported('Unsupported formula token: '+b.hex())

def inspect(raw: bytes) -> dict:
    w = workbook_stream(raw); rec = list(records(w)); sheets=[]; offsets={}; sst=[]; names=[]; externals=[]
    for op,b,p in rec:
        if op in (0x2f, 0x3c): raise Unsupported('Encrypted or CONTINUE workbook unsupported')
        if op == 0x85:
            name, _ = string(b, 6, short=True); sheets.append(name); offsets[u32(b)] = name
        elif op == 0xfc:
            at=8
            for _ in range(u32(b, 4)):
                s,at=string(b,at,rich=True); sst.append(s)
            if at != len(b): raise Unsupported('SST trailing bytes')
        elif op == 0x17:
            externals.extend(struct.unpack_from('<HHH', b, 2+i*6) for i in range(u16(b)))
        elif op == 0x18:
            n=b[3]; size=u16(b,4); flags=b[14]; stop=15+n*(2 if flags & 1 else 1)
            name=b[15:stop].decode('utf-16le' if flags & 1 else 'latin1')
            names.append({'name':name,'builtin':bool(u16(b)&0x20),'tokens':b[stop:stop+size]})
    cells={s:{} for s in sheets}; dv=[]; active=None
    for op,b,p in rec:
        if p in offsets: active=offsets[p]
        if not active: continue
        def put(r,c,v): cells[active][(r,c)]=v
        if op == 0xfd: put(u16(b),u16(b,2),sst[u32(b,6)])
        elif op == 0x203: put(u16(b),u16(b,2),struct.unpack_from('<d',b,6)[0])
        elif op == 0x27e: put(u16(b),u16(b,2),rk(u32(b,6)))
        elif op == 0xbd:
            r,c=u16(b),u16(b,2)
            for at in range(4,len(b)-2,6): put(r,c,rk(u32(b,at+2)));c+=1
        elif op == 0x1be:
            flags=u32(b);at=4;messages={}
            for k in ('prompt_title','error_title','prompt','error'):
                s,at=string(b,at);messages[k]=s.replace('\x00','')
            forms=[]
            for _ in range(2):
                n=u16(b,at);at+=4;tokens=b[at:at+n];at+=n
                forms.append(formula(tokens,names,externals,sheets))
            count=u16(b,at);at+=2;ranges=[]
            for _ in range(count):
                r1,r2,c1,c2=struct.unpack_from('<HHHH',b,at);at+=8
                ranges.append(cellname(r1,c1)+':'+cellname(r2,c2))
            if at != len(b): raise Unsupported('DV trailing bytes')
            dv.append({'sheet':active,'ranges':ranges,'type':flags&15,'operator':(flags>>20)&15,
                       'allow_blank':bool(flags&256),'show_error':bool(flags&(1<<19)),
                       'formula1':forms[0],'formula2':forms[1],**messages})
    catalogs={}; named={}
    for name in names:
        if name['builtin']: continue
        f=formula(name['tokens'],names,externals,sheets);named[name['name']]=f
        if isinstance(f,dict) and 'range' in f:
            r1,r2,c1,c2=f['range']
            catalogs[name['name']]=[[cells[f['sheet']].get((r,c)) for c in range(c1,c2+1)] for r in range(r1,r2+1)]
    headers=[cells['Ofertas'].get((0,c),'') for c in range(37)]
    # Do not export populated operational rows or file metadata.
    return {'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'biff':'BIFF8',
            'sheets':sheets,'headers':headers[:26],'auxiliary_headers':headers[26:],
            'validations':dv,'named_ranges':named,'catalogs':catalogs,
            'nonblank_input_cells_below_header':sum(1 for (r,c),v in cells['Ofertas'].items() if r>0 and c<26 and v not in ('',None))}

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('source',type=Path);parser.add_argument('output',type=Path);args=parser.parse_args()
    result=inspect(args.source.read_bytes());args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('AUDIT OK:',len(result['headers']),'headers;',len(result['validations']),'DV records; hash',result['sha256'])
