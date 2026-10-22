#!/usr/bin/env python3
"""Check task graph, links and portable package; read-only."""
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def check(root=ROOT):
    state=json.loads((root/'.project/STATE.json').read_text())
    tasks=state['tasks']; mapping={t['id']:t for t in tasks}; errors=[]
    if len(mapping)!=len(tasks): errors.append('duplicate task ID')
    valid={'TODO','READY','IN_PROGRESS','REVIEW','DONE','BLOCKED','CANCELLED'}
    for task in tasks:
        if task['status'] not in valid: errors.append('invalid status '+task['id'])
        if not (root/task['path']).is_file(): errors.append('missing task '+task['id'])
        for dep in task['depends_on']:
            if dep not in mapping: errors.append('unknown dependency '+dep)
            elif task['status'] in {'READY','IN_PROGRESS','REVIEW','DONE'} and mapping[dep]['status']!='DONE':
                errors.append('unfinished dependency '+task['id'])
    def visit(key,path):
        if key in path: raise ValueError('dependency cycle '+key)
        for dep in mapping[key]['depends_on']:
            if dep in mapping: visit(dep,path|{key})
    try:
        for key in mapping: visit(key,set())
    except ValueError as exc: errors.append(str(exc))
    files=list((root/'skills/xpo-operations').rglob('*.md'))+list((root/'.project').rglob('*.md'))+[root/'README.md',root/'ROUTE.md']
    for file in files:
        for target in re.findall(r'\]\(([^)]+)\)',file.read_text()):
            if '://' in target or target.startswith('#'): continue
            if not (file.parent/target.split('#')[0]).exists(): errors.append(f'broken link {file.relative_to(root)}: {target}')
    return errors
if __name__=='__main__':
    errors=check()
    if errors: raise SystemExit('\n'.join(errors))
    print('PASS: task dependencies, files and relative links')
