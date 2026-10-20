"""Cloudflare entrypoint; runtime SDK is explicitly vendored for modern dates."""
from workers import WorkerEntrypoint
from cloud_adapter.api import app


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        import asgi
        return await asgi.fetch(app, request, self.env)
