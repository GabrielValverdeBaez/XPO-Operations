"""Verify the published implementation is byte-identical to the locally tested snapshot."""
from pathlib import Path
import hashlib
import json
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'evidence/source-sha256.json').read_text())
failed=[name for name,expected in manifest.items() if hashlib.sha256((root/name).read_bytes()).hexdigest()!=expected]
if failed:raise SystemExit('Source snapshot differs: '+', '.join(failed))
print(f'PASS: {len(manifest)} implementation files match the tested snapshot')
