"""Local SQLite snapshots, duplicate detection, rules revisions and corridor tables."""
from __future__ import annotations
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
from .engine import DEFAULT_RULES, check_rules
from .models import Rules, CorridorRate

def dump(obj):return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'))

class Store:
    def __init__(self,path):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        with self.db() as db:
            version=db.execute('PRAGMA user_version').fetchone()[0]
            if version not in (0,1):raise ValueError('Version de base de datos no compatible: no modificar')
            db.executescript('''
            CREATE TABLE IF NOT EXISTS snapshots(id INTEGER PRIMARY KEY, identity TEXT NOT NULL,
                fingerprint TEXT NOT NULL UNIQUE, payload TEXT NOT NULL, created TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS by_identity ON snapshots(identity);
            CREATE TABLE IF NOT EXISTS rules(revision INTEGER PRIMARY KEY, payload TEXT NOT NULL, created TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS rates(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY, action TEXT NOT NULL, detail TEXT NOT NULL, created TEXT NOT NULL);
            PRAGMA user_version=1;
            ''')
            db.execute('INSERT OR IGNORE INTO rules VALUES(?,?,?)',(1,dump(DEFAULT_RULES.model_dump()),self.now()))
        os.chmod(self.path,0o600)
    @staticmethod
    def now():return datetime.now(timezone.utc).isoformat()
    @contextmanager
    def db(self):
        db=sqlite3.connect(self.path,timeout=5)
        try:
            with db:yield db
        finally:db.close()
    def rules(self):
        with self.db() as db:row=db.execute('SELECT payload FROM rules ORDER BY revision DESC LIMIT 1').fetchone()
        return Rules.model_validate_json(row[0])
    def rule_history(self):
        with self.db() as db:rows=db.execute('SELECT revision,payload,created FROM rules ORDER BY revision DESC').fetchall()
        return [{'revision':r,'rules':json.loads(p),'created':t} for r,p,t in rows]
    def update_rules(self,rules,expected_revision):
        check_rules(rules)
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            current=db.execute('SELECT MAX(revision) FROM rules').fetchone()[0]
            if current!=expected_revision or rules.revision!=current+1:raise ValueError('Conflicto de revision: recargar antes de guardar')
            db.execute('INSERT INTO rules VALUES(?,?,?)',(rules.revision,dump(rules.model_dump()),self.now()))
            db.execute('INSERT INTO audit(action,detail,created) VALUES(?,?,?)',('rules_update',str(rules.revision),self.now()))
        return rules
    def restore_rules(self,revision,expected_revision):
        with self.db() as db:r=db.execute('SELECT payload FROM rules WHERE revision=?',(revision,)).fetchone()
        if not r:raise ValueError('Revision inexistente')
        rules=Rules.model_validate_json(r[0]);rules.revision=expected_revision+1;rules.reason=f'Restauracion de revision {revision}'
        return self.update_rules(rules,expected_revision)
    def save(self,result):
        if not result['can_export']:raise ValueError('Guardar requiere revision y ausencia de errores')
        load=result['load'];semantic=dict(load);semantic.pop('source_hash',None)
        fingerprint=hashlib.sha256(dump({'load':semantic,'rules_revision':result['rules_revision'],'market_basis':result['market_basis']}).encode()).hexdigest()
        identity=dump([load['reference'],load['customer']])
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            duplicate=db.execute('SELECT id FROM snapshots WHERE fingerprint=?',(fingerprint,)).fetchone()
            if duplicate:return {'id':duplicate[0],'duplicate':True,'related':[]}
            related=[r[0] for r in db.execute('SELECT id FROM snapshots WHERE identity=?',(identity,))]
            c=db.execute('INSERT INTO snapshots(identity,fingerprint,payload,created) VALUES(?,?,?,?)',(identity,fingerprint,dump(result),self.now()))
            return {'id':c.lastrowid,'duplicate':False,'related':related}
    def history(self):
        with self.db() as db:rows=db.execute('SELECT id,payload,created FROM snapshots ORDER BY id DESC LIMIT 200').fetchall()
        return [{'id':i,'created':t,'reference':json.loads(p)['load']['reference'],'route':json.loads(p)['load']['origin']['locality']+' -> '+json.loads(p)['load']['destination']['locality']} for i,p,t in rows]
    def get(self,ident):
        with self.db() as db:row=db.execute('SELECT payload FROM snapshots WHERE id=?',(ident,)).fetchone()
        if not row:raise ValueError('Registro inexistente')
        return json.loads(row[0])
    def rates(self):
        with self.db() as db:rows=db.execute('SELECT payload FROM rates ORDER BY id').fetchall()
        return [CorridorRate.model_validate_json(x[0]) for x in rows]
    def set_rate(self,rate):
        with self.db() as db:
            db.execute('INSERT OR REPLACE INTO rates VALUES(?,?)',(rate.id,dump(rate.model_dump(mode='json'))))
            db.execute('INSERT INTO audit(action,detail,created) VALUES(?,?,?)',('rate_update',dump(rate.model_dump(mode='json')),self.now()))
    def backup(self,target):
        target=Path(target)
        if target.exists() or target.resolve()==self.path.resolve():raise ValueError('Backup debe ser un archivo nuevo')
        try:
            with self.db() as src:
                dst=sqlite3.connect(target)
                try:src.backup(dst)
                finally:dst.close()
            os.chmod(target,0o600)
        except Exception:
            target.unlink(missing_ok=True);raise
        return target
