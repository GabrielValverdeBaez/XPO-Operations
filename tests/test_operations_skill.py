import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT/'skills/xpo-operations/scripts'
def module(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS/(name+'.py'))
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value
OPS = module('operations')
WT = module('validate_wtransnet_rows')

def row():
    # Independent schema fixture: A..Z, fictitious reference and no commercial data.
    return ['TEST-001','22/10/2026','España','28001','Madrid','Portugal','0410','Destino ficticio','Tráilers Completos','Trailer','Carga General','5','13,6','','','','','','','','','','','Carga: 22/10/2026 de 08:00 a 09:00.','','']
def company():
    return ['Empresa ficticia - Madrid','Transportista','Carretera','FTL','Tautliner','España','Madrid / Madrid','28001','Madrid','Nacional','','','ops@example.com;','','','','','','']

class OperationsTests(unittest.TestCase):
    def test_emails_normalize_and_preserve_order(self):
        self.assertEqual(OPS.extract_emails('B@Example.com; a@example.com B@example.com'), ['b@example.com','a@example.com'])
    def test_email_blocked_case_insensitive(self):
        self.assertEqual(OPS.extract_emails('x@example.com y@example.com', ['X@example.com']), ['y@example.com'])
    def test_email_no_inference(self):
        self.assertEqual(OPS.extract_emails('Empresa sin correo'), [])
    def test_directory_valid(self):
        self.assertEqual(OPS.directory_errors('\t'.join(company())), [])
    def test_directory_rejects_wrong_width(self):
        self.assertTrue(OPS.directory_errors('foo\tbar'))
    def test_directory_rejects_service_as_mode(self):
        data=company(); data[2]='FTL'; self.assertTrue(OPS.directory_errors('\t'.join(data)))
    def test_directory_rejects_secondary(self):
        data=company(); data[13]='x'; self.assertTrue(OPS.directory_errors('\t'.join(data)))
    def test_directory_rejects_email_duplicates(self):
        data=company(); data[12]='ops@example.com; OPS@example.com;'; self.assertTrue(OPS.directory_errors('\t'.join(data)))
    def test_directory_pt_cp(self):
        data=company(); data[5]='Portugal'; data[7]='0410'; self.assertEqual(OPS.directory_errors('\t'.join(data)), [])
        data[7]='0410-001'; self.assertTrue(OPS.directory_errors('\t'.join(data)))
    def test_wtransnet_valid_and_trailing_tabs(self):
        data='\t'.join(row()); self.assertTrue(data.endswith('\t\t')); self.assertEqual(WT.validate_row(data,2), [])
    def test_wtransnet_rejects_25_columns(self):
        self.assertTrue(WT.validate_row('\t'.join(row()[:-1]),2))
    def test_wtransnet_impossible_date(self):
        data=row(); data[1]='31/02/2026'; self.assertTrue(WT.validate_row('\t'.join(data),2))
    def test_wtransnet_requires_date(self):
        data=row(); data[1]=''; self.assertTrue(WT.validate_row('\t'.join(data),2))
    def test_wtransnet_price_always_empty(self):
        data=row(); data[24]='10'; self.assertTrue(WT.validate_row('\t'.join(data),2))
    def test_wtransnet_rejects_speciality_and_bool(self):
        for index,value in [(10,'Tautliner'),(13,'True'),(25,'Sí')]:
            data=row(); data[index]=value; self.assertTrue(WT.validate_row('\t'.join(data),2))
    def test_wtransnet_rejects_invalid_numbers(self):
        for value in ['nan','inf','0','-1','1.5']:
            data=row(); data[11]=value; self.assertTrue(WT.validate_row('\t'.join(data),2))
    def test_wtransnet_rejects_country_cp_mismatch(self):
        data=row(); data[3]='2800'; self.assertTrue(WT.validate_row('\t'.join(data),2))
    def test_wtransnet_cli_empty_and_51_rejected(self):
        for payload in ['', '\n'.join(['\t'.join(row())]*51)]:
            result=subprocess.run([sys.executable,str(SCRIPTS/'validate_wtransnet_rows.py')],input=payload,text=True,capture_output=True)
            self.assertEqual(result.returncode,1)
    def test_cli_extract_with_private_blocklist(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            block=Path(directory)/'blocked.txt'; block.write_text('a@example.com')
            result=subprocess.run([sys.executable,str(SCRIPTS/'operations.py'),'emails','--blocked',str(block)],input='A@example.com b@example.com',text=True,capture_output=True)
            self.assertEqual(result.returncode,0); self.assertEqual(result.stdout.strip(),'b@example.com;')
    def test_cli_directory(self):
        result=subprocess.run([sys.executable,str(SCRIPTS/'operations.py'),'directory'],input='\t'.join(company()),text=True,capture_output=True)
        self.assertEqual(result.returncode,0)

if __name__ == '__main__':
    unittest.main()
