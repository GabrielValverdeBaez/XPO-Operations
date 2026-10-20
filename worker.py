"""Module-level entrypoint compatible with the Python runtime bundled by Wrangler."""
from cloud_adapter.api import app


async def on_fetch(request, env):
    import asgi
    return await asgi.fetch(app, request, env)
