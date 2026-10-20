"""Small repository-local DAG/state consistency check. Full Project Route QA is separate."""
from pathlib import Path
import yaml
root=Path(__file__).resolve().parents[1]
def meta(path):return yaml.safe_load(path.read_text().split('---',2)[1])
tasks={}
for file in sorted((root/'TASKS').glob('*.md')):
    t=meta(file);assert t['id'] not in tasks;tasks[t['id']]=t
assert tasks
for k,t in tasks.items():
    assert t['status'] in {'TODO','READY','IN_PROGRESS','REVIEW','DONE','BLOCKED','CANCELLED'},k
    assert t['objective_refs'] and t['produces'],k
    assert all(d in tasks and d!=k for d in t['depends_on']),k
    if t['status'] in {'READY','DONE'}:
        assert all(tasks[d]['status']=='DONE' for d in t['depends_on']),k
seen=set();active=set()
def visit(k):
    assert k not in active,'Cycle: '+k
    if k in seen:return
    active.add(k)
    for d in tasks[k]['depends_on']:visit(d)
    active.remove(k);seen.add(k)
for k in tasks:visit(k)
print('PASS: task IDs, states, dependencies and DAG')
