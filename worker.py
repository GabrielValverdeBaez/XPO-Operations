"""Cloudflare ASGI entrypoint with the explicitly vendored runtime SDK."""
from workers import asgi
from cloud_adapter.api import app

Default = asgi.entrypoint(app)
