import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from datetime import datetime,timezone,timedelta
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('project_cache',ROOT/'skills/xpo-operations/scripts/project_cache.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def row(name='Synthetic Carrier',route='Madrid → Sevilla',email='ops@example.com;'):
 return [name,'Transportista','Carretera','FTL','Tautliner','España','Madrid','28001','Madrid','España',route,'',email,'','','','','','']
class CacheTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.c=m.Cache(Path(self.tmp.name)/'cache.sqlite3');self.c.source('test','v1')
 def tearDown(self): self.c.close();self.tmp.cleanup()
 def test_idempotent_record_and_emails(self):
  for _ in range(2): self.c.record('test',1,row(email='OPS@EXAMPLE.COM; ops@example.com;'))
  self.assertEqual(self.c.stats()['records'],1);self.assertEqual(self.c.query('Andalucía')['emails'],['ops@example.com'])
 def test_city_alias_and_accent(self):
  self.c.record('test',1,row(route='Madrid → Culleredo'))
  self.assertEqual(len(self.c.query('Galicia')['carriers']),1)
 def test_no_inference_from_headquarters_or_name(self):
  a=row('Galicia Logistics',route='Madrid → Valencia');a[6]='Galicia';a[8]='Vigo';self.c.record('test',1,a)
  self.assertEqual(self.c.query('Galicia')['emails'],[])
 def test_no_substring_false_positive(self):
  self.c.record('test',1,row(route='Madrid → Sevillana de Prueba'))
  self.assertEqual(self.c.query('Andalucía')['emails'],[])
 def test_coverage_is_distinct(self):
  a=row(route='Madrid → Valencia');a[9]='Galicia';self.c.record('test',1,a)
  self.assertEqual(self.c.query('Galicia')['emails'],[])
  self.assertEqual(self.c.query('Galicia','coverage')['emails'],['ops@example.com'])
 def test_declared_does_not_become_history(self):
  self.c.record('test',1,row());self.assertEqual(self.c.query('Andalucía','history')['emails'],[])
 def test_history_direction_and_delivered_only(self):
  self.c.record('test',1,row());self.c.trip('test','Synthetic Carrier','Sevilla','Madrid','T1',state='assigned')
  self.assertEqual(len(self.c.query('Andalucía','history','from')['emails']),1)
  self.assertEqual(self.c.query('Andalucía','history','to')['emails'],[])
  self.assertEqual(self.c.query('Andalucía','delivered')['emails'],[])
  self.c.trip('test','Synthetic Carrier','Sevilla','Madrid','T1',state='delivered')
  self.assertEqual(len(self.c.query('Andalucía','delivered')['emails']),1);self.assertEqual(self.c.stats()['trips'],1)
 def test_provisional_and_cancelled_not_verified(self):
  self.c.record('test',1,row())
  for state in ['provisional','cancelled']:
   self.c.trip('test','Synthetic Carrier','Madrid','Sevilla',state=state)
   self.assertEqual(self.c.query('Andalucía','history')['emails'],[])
 def test_email_exclusion(self):
  self.c.record('test',1,row());self.c.exclude('email','OPS@EXAMPLE.COM','bounce','test')
  self.assertEqual(self.c.query('Andalucía')['emails'],[])
 def test_red_any_record_excludes_company(self):
  self.c.record('test',1,row());self.c.record('test',2,row(route='Madrid → Galicia'),controls='blocked')
  self.assertEqual(self.c.query('Andalucía')['emails'],[])
 def test_carrier_exclusion_handles_delegation(self):
  self.c.record('test',1,row('Synthetic Carrier - Madrid'));self.c.exclude('carrier','Synthetic Carrier','blocked','test')
  self.assertEqual(self.c.query('Andalucía')['emails'],[])
 def test_unknown_and_stale_not_approved(self):
  self.c.record('test',1,row());self.assertEqual(self.c.query('Andalucía',approved_only=True)['emails'],[])
  self.c.record('test',1,row(),controls='checked',checked_at=(datetime.now(timezone.utc)-timedelta(days=2)).isoformat())
  self.assertEqual(self.c.query('Andalucía',approved_only=True)['emails'],[])
  self.c.record('test',1,row(),controls='checked',checked_at=m.now())
  self.assertEqual(self.c.query('Andalucía',approved_only=True)['emails'],['ops@example.com'])
 def test_future_check_not_approved(self):
  self.c.record('test',1,row(),controls='checked',checked_at=(datetime.now(timezone.utc)+timedelta(days=1)).isoformat())
  self.assertEqual(self.c.query('Andalucía',approved_only=True)['emails'],[])
 def test_exact_money_and_no_revenue_to_cost(self):
  self.c.operation('test','O1','2026-10-23','Madrid','Sevilla',client_revenue='1084.29')
  r=self.c.db.execute('SELECT * FROM operations').fetchone()
  self.assertEqual(r['client_revenue'],'1084.29');self.assertIsNone(r['carrier_cost']);self.assertIsNone(r['market_estimate'])
 def test_no_lost_amount_on_partial_update(self):
  self.c.operation('test','O1','2026-10-23','Madrid','Sevilla',client_revenue='10.01')
  self.c.operation('test','O1','2026-10-23','Madrid','Sevilla',observations='Synthetic note')
  self.assertEqual(self.c.db.execute('SELECT client_revenue FROM operations').fetchone()[0],'10.01')
 def test_bad_money_rejected(self):
  for value in ['NaN','Infinity','-1','12.345']:
   with self.assertRaises(ValueError): m.money(value)
 def test_notes_survive_refresh(self):
  self.c.record('test',1,row());self.c.observation('test','carrier','Synthetic Carrier','Keep this note','2026-10-22T10:00:00Z')
  self.c.operation('test','O1','2026-10-23','Madrid','Sevilla',client_revenue='15')
  self.c.source('test','v2');self.assertEqual(self.c.stats()['records'],0)
  self.assertEqual(self.c.stats()['observations'],1);self.assertEqual(self.c.stats()['operations'],1)
 def test_export_restore_and_content_equivalence(self):
  self.c.record('test',1,row());path=Path(self.tmp.name)/'snapshot.json';data=self.c.snapshot(path)
  restored=m.Cache(Path(self.tmp.name)/'restored.sqlite3')
  try:
   restored.restore(json.loads(path.read_text()));self.assertEqual(restored.query('Andalucía')['emails'],['ops@example.com'])
   self.assertEqual(data['tables'],restored.snapshot(Path(self.tmp.name)/'again.json')['tables'])
  finally: restored.close()
 def test_restore_refuses_nonempty(self):
  data=self.c.snapshot(Path(self.tmp.name)/'snap.json')
  with self.assertRaises(ValueError): self.c.restore(data)
 def test_unknown_region_and_unstructured_direction(self):
  with self.assertRaises(ValueError): self.c.query('unknown')
  with self.assertRaises(ValueError): self.c.query('Galicia','declared','to')
 def test_sales_separates_available_from_executed(self):
  self.c.operation('test','O1','2026-10-23','Madrid','Sevilla',state='available',customer='Synthetic Customer',client_revenue='100')
  self.assertEqual(len(self.c.sales('Andalucía','Synthetic')),1)
  self.assertEqual(self.c.sales(completed_only=True),[])
  self.c.operation('test','O2','2026-10-24','Madrid','Sevilla',state='delivered',customer='Synthetic Customer',client_revenue='100',carrier_cost='80',carrier_name='Synthetic Carrier')
  actual=self.c.sales(completed_only=True)
  self.assertEqual(len(actual),1);self.assertEqual(actual[0]['carrier_name'],'Synthetic Carrier');self.assertEqual(actual[0]['carrier_cost'],'80.00')
 def test_transaction_rollback(self):
  self.c.db.commit()
  with self.assertRaises(ValueError):
   with self.c.db:
    self.c.record('test',1,row());self.c.record('test',2,['bad'])
  self.assertEqual(self.c.stats()['records'],0)
if __name__=='__main__': unittest.main()
