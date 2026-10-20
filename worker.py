"""Entry point copied by build_cloudflare.py into the isolated deployment bundle."""
from workers import asgi
from cloud_adapter.api import app
Default = asgi.entrypoint(app)
