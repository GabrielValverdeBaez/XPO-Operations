"""Async D1 store. Atomic batches and conditional writes; no local filesystem."""
from datetime import datetime, timezone
import hashlib
import json
from loadstudio.engine import DEFAULT_RULES, check_rules
from loadstudio.models import Rules, CorridorRate


def dump(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def native(obj):
    return obj.to_py() if hasattr(obj, 'to_py') else obj


def js_array(values):
    try:
        from pyodide.ffi import to_js
    except ImportError:
        return values  # Native tests use the same SQL with a SQLite binding double.
    return to_js(values)


SCHEMA = [
    'CREATE TABLE IF NOT EXISTS xpo_meta (id INTEGER PRIMARY KEY CHECK(id=1), version INTEGER NOT NULL)',
    'CREATE TABLE IF NOT EXISTS snapshots(id INTEGER PRIMARY KEY, identity TEXT NOT NULL, fingerprint TEXT NOT NULL UNIQUE, payload TEXT NOT NULL, created TEXT NOT NULL)',
    'CREATE INDEX IF NOT EXISTS by_identity ON snapshots(identity)',
    'CREATE TABLE IF NOT EXISTS rules(revision INTEGER PRIMARY KEY, payload TEXT NOT NULL, created TEXT NOT NULL)',
    'CREATE TABLE IF NOT EXISTS rates(id TEXT PRIMARY KEY, payload TEXT NOT NULL)',
    'CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY, action TEXT NOT NULL, detail TEXT NOT NULL, created TEXT NOT NULL)',
    "CREATE TRIGGER IF NOT EXISTS audit_rule AFTER INSERT ON rules BEGIN INSERT INTO audit(action,detail,created) VALUES('rules_update',CAST(NEW.revision AS TEXT),NEW.created); END",
    'INSERT OR IGNORE INTO xpo_meta VALUES(1,1)',
]


class D1Store:
    def __init__(self, binding):
        self.db = binding

    @staticmethod
    def now():
        return datetime.now(timezone.utc).isoformat()

    def statement(self, sql, *args):
        stmt = self.db.prepare(sql)
        return stmt.bind(*args) if args else stmt

    async def rows(self, sql, *args):
        result = native(await self.statement(sql, *args).all())
        if not result.get('success', True):
            raise RuntimeError('D1 query failed')
        return result['results']

    async def batch(self, statements):
        result = native(await self.db.batch(js_array(statements)))
        if any(not item.get('success', True) for item in result):
            raise RuntimeError('D1 batch failed')
        return result

    async def ensure(self):
        # No destructive migrations. Existing future schemas are refused.
        await self.batch([self.statement(sql) for sql in SCHEMA[:1]])
        version = await self.rows('SELECT version FROM xpo_meta WHERE id=1')
        if version and version[0]['version'] != 1:
            raise ValueError('Version D1 no compatible: no modificar')
        statements = [self.statement(sql) for sql in SCHEMA[1:]]
        statements.append(self.statement('INSERT OR IGNORE INTO rules VALUES(?,?,?)', 1, dump(DEFAULT_RULES.model_dump()), self.now()))
        await self.batch(statements)
        return self

    async def rules(self):
        rows = await self.rows('SELECT payload FROM rules ORDER BY revision DESC LIMIT 1')
        return Rules.model_validate_json(rows[0]['payload'])

    async def rule_history(self):
        rows = await self.rows('SELECT revision,payload,created FROM rules ORDER BY revision DESC')
        return [{'revision':r['revision'], 'rules':json.loads(r['payload']), 'created':r['created']} for r in rows]

    async def update_rules(self, rules, expected_revision):
        check_rules(rules)
        if rules.revision != expected_revision + 1:
            raise ValueError('Conflicto de revision: recargar antes de guardar')
        # One SQL statement is the compare-and-swap, including concurrent callers.
        inserted = await self.rows('''INSERT INTO rules(revision,payload,created)
            SELECT ?,?,? WHERE (SELECT MAX(revision) FROM rules)=?
            ON CONFLICT(revision) DO NOTHING RETURNING revision''',
            rules.revision, dump(rules.model_dump()), self.now(), expected_revision)
        if not inserted:
            raise ValueError('Conflicto de revision: recargar antes de guardar')
        return rules

    async def restore_rules(self, revision, expected_revision):
        rows = await self.rows('SELECT payload FROM rules WHERE revision=?', revision)
        if not rows:
            raise ValueError('Revision inexistente')
        rules = Rules.model_validate_json(rows[0]['payload'])
        rules.revision = expected_revision + 1
        rules.reason = f'Restauracion de revision {revision}'
        return await self.update_rules(rules, expected_revision)

    async def save(self, result):
        if not result['can_export']:
            raise ValueError('Guardar requiere revision y ausencia de errores')
        load = result['load']
        semantic = dict(load)
        semantic.pop('source_hash', None)
        fingerprint = hashlib.sha256(dump({'load':semantic, 'rules_revision':result['rules_revision'], 'market_basis':result['market_basis']}).encode()).hexdigest()
        identity = dump([load['reference'], load['customer']])
        rows = await self.batch([
            self.statement('INSERT INTO snapshots(identity,fingerprint,payload,created) VALUES(?,?,?,?) ON CONFLICT(fingerprint) DO NOTHING RETURNING id', identity, fingerprint, dump(result), self.now()),
            self.statement('SELECT id FROM snapshots WHERE fingerprint=?', fingerprint),
            self.statement('SELECT id FROM snapshots WHERE identity=? ORDER BY id', identity),
        ])
        ident = rows[1]['results'][0]['id']
        duplicate = not bool(rows[0]['results'])
        return {'id':ident, 'duplicate':duplicate, 'related':[] if duplicate else [r['id'] for r in rows[2]['results'] if r['id'] != ident]}

    async def history(self):
        rows = await self.rows('SELECT id,payload,created FROM snapshots ORDER BY id DESC LIMIT 200')
        return [{'id':r['id'], 'created':r['created'], 'reference':json.loads(r['payload'])['load']['reference'],
                 'route':json.loads(r['payload'])['load']['origin']['locality']+' -> '+json.loads(r['payload'])['load']['destination']['locality']} for r in rows]

    async def get(self, ident):
        rows = await self.rows('SELECT payload FROM snapshots WHERE id=?', ident)
        if not rows:
            raise ValueError('Registro inexistente')
        return json.loads(rows[0]['payload'])

    async def rates(self):
        rows = await self.rows('SELECT payload FROM rates ORDER BY id')
        return [CorridorRate.model_validate_json(row['payload']) for row in rows]

    async def set_rate(self, rate):
        payload = dump(rate.model_dump(mode='json'))
        await self.batch([
            self.statement('INSERT INTO rates(id,payload) VALUES(?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload', rate.id, payload),
            self.statement('INSERT INTO audit(action,detail,created) VALUES(?,?,?)', 'rate_update', payload, self.now()),
        ])

    async def backup(self):
        tables = ('xpo_meta','snapshots','rules','rates','audit')
        # Atomic export; never silently truncate a large backup.
        result = await self.batch([self.statement('SELECT * FROM '+table+' LIMIT 10001') for table in tables])
        if any(len(r['results']) > 10000 for r in result):
            raise ValueError('Exportacion grande: usar export D1 del panel, sin truncar datos')
        data = {'format':'xpo-d1-backup', 'version':1, 'created':self.now(),
                'tables':{name:r['results'] for name,r in zip(tables,result)}}
        if len(dump(data).encode()) > 20_000_000:
            raise ValueError('Exportacion grande: usar export D1 del panel')
        return data
