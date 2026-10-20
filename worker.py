"""Cloudflare ASGI entrypoint with the explicitly vendored runtime SDK."""
import sys
import workers
from workers import asgi
from cloud_adapter.api import app

if not hasattr(asgi, 'entrypoint'):
    # Package metadata only: never inspect request data, bindings, or secrets.
    raise RuntimeError('SDK resolution diagnostic: ' + repr({
        'workers_file': getattr(workers, '__file__', None),
        'asgi_file': getattr(asgi, '__file__', None),
        'workers_symbols': [n for n in dir(workers) if not n.startswith('_')],
        'asgi_symbols': [n for n in dir(asgi) if not n.startswith('_')],
        'sys_path': sys.path,
    }))

Default = asgi.entrypoint(app)
