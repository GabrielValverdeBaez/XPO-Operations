"""Explicit ASGI entrypoint supported by the deployed Workers runtime SDK."""
from workers import WorkerEntrypoint, asgi
from cloud_adapter.api import app


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        return await asgi.fetch(app, request, self.env)
